#!/usr/bin/env python3
"""
Day One to Apple Notes Import Tool

Imports Day One journal entries into Apple Notes, preserving text, images, videos,
tags, and metadata.
"""

import json
import os
import sys
import subprocess
import hashlib
import logging
import argparse
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DayOneParser:
    """Parses Day One JSON export files."""
    
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.entries = []
    
    def parse(self) -> List[Dict]:
        """Parse the Day One JSON export and return entries."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'entries' not in data:
                raise ValueError("JSON file does not contain 'entries' array")
            
            self.entries = data['entries']
            logger.info(f"Parsed {len(self.entries)} entries from {self.json_path}")
            return self.entries
        
        except FileNotFoundError:
            logger.error(f"JSON file not found: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.json_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    @staticmethod
    def get_entry_data(entry: Dict) -> Dict:
        """Extract relevant data from an entry."""
        return {
            'uuid': entry.get('uuid', ''),
            'text': entry.get('text', ''),
            'creationDate': entry.get('creationDate', ''),
            'photos': entry.get('photos', []),
            'videos': entry.get('videos', []),
            'tags': entry.get('tags', [])
        }


class MediaResolver:
    """Resolves media files from Day One export directories."""

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        self.photos_dir = export_dir / 'photos'
        self.videos_dir = export_dir / 'videos'
        self.photo_index = {}  # identifier -> path
        self.video_index = {}  # identifier -> path
        self.photo_files = []  # all photo files for lazy MD5 lookup
        self.video_files = []  # all video files for lazy MD5 lookup
        self._md5_cache = {}   # path -> md5 (computed on demand)
        self._build_indexes()

    def _build_indexes(self):
        """Build indexes of media files by identifier only (lazy MD5)."""
        if self.photos_dir.exists():
            self._index_directory(self.photos_dir, self.photo_index, self.photo_files)
            logger.info(f"Indexed {len(self.photo_index)} photo identifiers ({len(self.photo_files)} files)")
        else:
            logger.warning(f"Photos directory not found: {self.photos_dir}")

        if self.videos_dir.exists():
            self._index_directory(self.videos_dir, self.video_index, self.video_files)
            logger.info(f"Indexed {len(self.video_index)} video identifiers ({len(self.video_files)} files)")
        else:
            logger.warning(f"Videos directory not found: {self.videos_dir}")

    def _index_directory(self, directory: Path, index: Dict, file_list: List):
        """Index files by identifier only - MD5 calculated lazily on demand."""
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_list.append(file_path)
                # Only index by identifier (fast - no file reading)
                identifier = self._extract_identifier_from_filename(file_path.name)
                if identifier:
                    index[identifier.upper()] = file_path
    
    def _extract_identifier_from_filename(self, filename: str) -> Optional[str]:
        """Extract identifier from filename (may be in filename or need to check file)."""
        # Remove extension
        base = Path(filename).stem
        # If it looks like a hex identifier (32 chars), use it
        if len(base) == 32 and all(c in '0123456789ABCDEFabcdef' for c in base):
            return base
        return None
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file (cached)."""
        if file_path in self._md5_cache:
            return self._md5_cache[file_path]

        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        result = hash_md5.hexdigest().upper()
        self._md5_cache[file_path] = result
        return result

    def _find_by_md5(self, md5: str, file_list: List[Path]) -> Optional[Path]:
        """Lazily search for a file by MD5 hash."""
        if not md5:
            return None
        for file_path in file_list:
            try:
                if self._calculate_md5(file_path) == md5:
                    return file_path
            except Exception as e:
                logger.debug(f"Could not calculate MD5 for {file_path}: {e}")
        return None

    def resolve_photo(self, photo: Dict) -> Optional[Path]:
        """Resolve a photo object to a file path."""
        identifier = photo.get('identifier', '').upper()
        md5 = photo.get('md5', '').upper()

        # Try identifier first (fast - already indexed)
        if identifier and identifier in self.photo_index:
            return self.photo_index[identifier]

        # Try direct filename match
        if identifier:
            for file_path in self.photo_files:
                if identifier in file_path.name.upper():
                    return file_path

        # Last resort: lazy MD5 lookup (slow - only if needed)
        if md5:
            logger.debug(f"Falling back to MD5 lookup for photo: {md5[:8]}...")
            return self._find_by_md5(md5, self.photo_files)

        return None

    def resolve_video(self, video: Dict) -> Optional[Path]:
        """Resolve a video object to a file path."""
        identifier = video.get('identifier', '').upper()
        md5 = video.get('md5', '').upper()

        # Try identifier first (fast - already indexed)
        if identifier and identifier in self.video_index:
            return self.video_index[identifier]

        # Try direct filename match
        if identifier:
            for file_path in self.video_files:
                if identifier in file_path.name.upper():
                    return file_path

        # Last resort: lazy MD5 lookup (slow - only if needed)
        if md5:
            logger.debug(f"Falling back to MD5 lookup for video: {md5[:8]}...")
            return self._find_by_md5(md5, self.video_files)

        return None


class MarkdownConverter:
    """Converts markdown text to HTML for Apple Notes."""

    def __init__(self):
        self.md = None
        self._init_markdown()

    def _init_markdown(self):
        """Initialize markdown processor with error handling."""
        try:
            import markdown
            # Enable extensions for common Day One formatting
            self.md = markdown.Markdown(extensions=[
                'nl2br',       # newlines to <br>
                'sane_lists'   # better list handling
            ])
        except ImportError:
            logger.warning("markdown library not available, using plain text fallback")
            self.md = None

    def convert(self, text: str) -> str:
        """Convert markdown to HTML, with fallback to plain text."""
        # Preprocess: remove Day One specific image references (handled as attachments)
        text = self._preprocess_dayone_markdown(text)

        if self.md is None:
            return self._plain_text_to_html(text)

        try:
            self.md.reset()  # Reset state between conversions
            html = self.md.convert(text)
            return html
        except Exception as e:
            logger.warning(f"Markdown conversion failed: {e}")
            return self._plain_text_to_html(text)

    def _preprocess_dayone_markdown(self, text: str) -> str:
        """Remove Day One specific markdown that won't render."""
        import re
        # Remove Day One image references (handled as attachments)
        text = re.sub(r'!\[.*?\]\(dayone-moment://[^)]+\)', '', text)
        return text

    def _plain_text_to_html(self, text: str) -> str:
        """Fallback: convert plain text to basic HTML."""
        import html
        escaped = html.escape(text)
        # Convert newlines to <br>
        return escaped.replace('\n', '<br>\n')


class NotesCreator:
    """Creates notes in Apple Notes using AppleScript."""

    def __init__(self, folder_name: Optional[str] = None, dry_run: bool = False):
        self.folder_name = folder_name
        self.dry_run = dry_run
        self.created_notes = {}  # Track created notes for duplicate detection
        self.markdown_converter = MarkdownConverter()
    
    def _escape_applescript_string(self, text: str) -> str:
        """Escape special characters for AppleScript string literals."""
        # Replace backslashes first
        text = text.replace('\\', '\\\\')
        # Replace quotes
        text = text.replace('"', '\\"')
        return text
    
    def _format_text_for_applescript_body(self, text: str) -> str:
        """Format text for AppleScript body assignment, converting markdown to HTML.

        Apple Notes body property accepts HTML, which renders headers, bold,
        italic, and lists properly. Raw markdown would display as plain text.
        """
        # Convert markdown to HTML
        html = self.markdown_converter.convert(text)
        # Escape for AppleScript string
        escaped = self._escape_applescript_string(html)
        return f'"{escaped}"'

    def _execute_applescript(self, script: str) -> Tuple[bool, str]:
        """Execute AppleScript and return success status and output."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute AppleScript:\n{script[:200]}...")
            return True, "dry-run"
        
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, error_msg
        
        except subprocess.TimeoutExpired:
            return False, "AppleScript execution timed out"
        except Exception as e:
            return False, str(e)
    
    def check_notes_running(self) -> Tuple[bool, str]:
        """Check if Apple Notes is running, and launch it if not.

        Returns:
            Tuple of (is_running, message). If launch fails, message contains error details.
        """
        if self.dry_run:
            return True, "dry-run"

        # Check if Notes is running
        check_script = '''
        tell application "System Events"
            set notesRunning to (name of processes) contains "Notes"
            return notesRunning
        end tell
        '''

        success, output = self._execute_applescript(check_script)

        if not success:
            return False, f"Could not check Notes app status: {output}"

        is_running = output.strip().lower() == "true"

        if is_running:
            return True, "Notes app is running"

        # Notes is not running, launch it
        logger.info("Apple Notes is not running, launching...")

        launch_script = '''
        tell application "Notes"
            activate
        end tell
        delay 2
        tell application "System Events"
            set notesRunning to (name of processes) contains "Notes"
            return notesRunning
        end tell
        '''

        success, output = self._execute_applescript(launch_script)

        if not success:
            return False, f"Failed to launch Notes app: {output}"

        is_running = output.strip().lower() == "true"

        if not is_running:
            return False, "Notes app failed to launch. Please open it manually and try again."

        return True, "Notes app launched"
    
    def ensure_folder_exists(self) -> bool:
        """Ensure the target folder exists in Apple Notes, creating it if needed."""
        if not self.folder_name:
            return True  # Use default folder
        
        script = f'''
        tell application "Notes"
            try
                set folderList to name of folders
                if folderList does not contain "{self.folder_name}" then
                    make new folder with properties {{name:"{self.folder_name}"}}
                end if
                return true
            on error errMsg
                return false
            end try
        end tell
        '''
        
        success, output = self._execute_applescript(script)
        if not success:
            logger.warning(f"Could not ensure folder '{self.folder_name}' exists: {output}")
        return success
    
    def _format_date_for_display(self, creation_date: str) -> Optional[str]:
        """Format an ISO date string for human-readable display in note body."""
        if not creation_date:
            return None

        try:
            cleaned = creation_date.strip()
            if cleaned.endswith('Z'):
                cleaned = cleaned[:-1] + '+00:00'
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is not None:
                dt = dt.astimezone()
            # Format: "May 15, 2023 at 10:30 AM"
            return dt.strftime('%B %d, %Y at %I:%M %p').replace(' 0', ' ').replace(' at 0', ' at ')
        except Exception as e:
            logger.warning(f"Could not parse creation date '{creation_date}': {e}")
            return None

    def create_note(self, text: str, photos: List[Path], videos: List[Path],
                   tags: List[str], creation_date: Optional[str] = None,
                   entry_uuid: str = '') -> Tuple[bool, str]:
        """Create a note in Apple Notes with text and attachments."""

        # Prepend creation date to note body (Apple Notes doesn't allow setting creation date)
        if creation_date:
            formatted_date = self._format_date_for_display(creation_date)
            if formatted_date:
                text = f"📅 {formatted_date}\n\n{text}"
            else:
                # Fallback to raw date if parsing failed
                text = f"📅 {creation_date}\n\n{text}"

        # Check for duplicates and generate unique title
        title = self._extract_title(text)
        note_title = self._get_unique_title(title)

        # Ensure folder exists
        if self.folder_name:
            self.ensure_folder_exists()

        # Build AppleScript
        script_parts = ['tell application "Notes"']

        # Get or create folder
        if self.folder_name:
            script_parts.append(f'set targetFolder to folder "{self.folder_name}"')
        else:
            script_parts.append('set targetFolder to folder 1')  # Default folder

        # Create note with properly formatted text (preserves newlines and markdown)
        body_text_expr = self._format_text_for_applescript_body(text)
        script_parts.append(f'set noteBody to {body_text_expr}')
        script_parts.append(f'make new note at targetFolder with properties {{body:noteBody}}')
        script_parts.append('set newNote to result')

        # Add attachments (photos first, then videos, maintaining order)
        all_media = [(p, 'photo') for p in photos] + [(v, 'video') for v in videos]
        for media_path, media_type in all_media:
            if media_path and media_path.exists():
                abs_path = str(media_path.absolute()).replace('\\', '\\\\')
                # Use "make new attachment at note with data" syntax
                script_parts.append(f'''
                try
                    set mediaFile to POSIX file "{abs_path}" as alias
                    make new attachment at newNote with data mediaFile
                on error errMsg
                    log "Failed to attach {media_type}: " & errMsg
                end try
                ''')
        
        # Add tags - Apple Notes recognizes hashtags in body text as tags
        # Use hashtag format directly in body (most reliable method across macOS versions)
        if tags:
            escaped_tags = [self._escape_applescript_string(tag) for tag in tags]
            # Build hashtag string: "#tag1 #tag2 #tag3"
            hashtag_string = ' '.join([f'#{tag}' for tag in escaped_tags])
            escaped_hashtag_string = self._escape_applescript_string(hashtag_string)
            script_parts.append(f'''
            try
                -- Add hashtags to body (Notes recognizes these as tags)
                set currentBody to body of newNote
                set tagString to return & return & "{escaped_hashtag_string}"
                set body of newNote to currentBody & tagString
            on error errMsg
                log "Failed to add tags: " & errMsg
            end try
            ''')
        
        script_parts.append('end tell')
        script = '\n'.join(script_parts)
        
        success, output = self._execute_applescript(script)
        
        if success:
            # Track created note
            self.created_notes[note_title] = self.created_notes.get(note_title, 0) + 1
            logger.info(f"Created note: {note_title}")
        else:
            logger.error(f"Failed to create note '{note_title}': {output}")
        
        return success, output
    
    def _extract_title(self, text: str) -> str:
        """Extract a title from note text (first line or first 50 chars)."""
        lines = text.strip().split('\n')
        if lines:
            title = lines[0].strip()
            if len(title) > 50:
                title = title[:47] + '...'
            return title if title else "Untitled Note"
        return "Untitled Note"
    
    def _get_unique_title(self, base_title: str) -> str:
        """Get a unique title, appending numbers for duplicates."""
        if base_title not in self.created_notes:
            self.created_notes[base_title] = 0
            return base_title
        
        self.created_notes[base_title] += 1
        count = self.created_notes[base_title]
        return f"{base_title} {count + 1}"


class DayOneImporter:
    """Main importer class that orchestrates the import process."""
    
    def __init__(self, export_dir: Path, folder_name: Optional[str] = None, 
                 dry_run: bool = False, verbose: bool = False, 
                 selected_files: Optional[List[Path]] = None,
                 use_tui: bool = False,
                 limit: Optional[int] = None):
        self.export_dir = Path(export_dir)
        self.folder_name = folder_name
        self.dry_run = dry_run
        self.verbose = verbose
        self.limit = limit
        self.use_tui = use_tui and RICH_AVAILABLE
        self.console = Console() if self.use_tui else None
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Find JSON files in export directory
        all_json_files = list(self.export_dir.glob('*.json'))
        if not all_json_files:
            raise ValueError(f"No JSON files found in {export_dir}")
        
        # Use selected files if provided, otherwise use all
        if selected_files:
            self.json_files = [f for f in all_json_files if f in selected_files]
        else:
            self.json_files = all_json_files
        
        if not self.json_files:
            raise ValueError("No JSON files selected for import")
        
        self.parser = None
        self.resolver = MediaResolver(self.export_dir)
        self.notes_creator = NotesCreator(folder_name, dry_run)
        
        self.stats = {
            'total_entries': 0,
            'successful': 0,
            'failed': 0,
            'missing_media': []
        }
        
        self.cancelled = False
    
    def import_all(self):
        """Import all entries from selected JSON files."""
        # Pre-flight check: Ensure Notes app is running (launches if needed)
        is_running, message = self.notes_creator.check_notes_running()
        if not is_running:
            error_msg = f"Pre-import check failed: {message}"
            if self.use_tui and self.console:
                self.console.print(f"[red]Error:[/red] {error_msg}")
                self.console.print("\n[yellow]Please open Apple Notes app and try again.[/yellow]")
            else:
                logger.error(error_msg)
                print(f"\nError: {error_msg}")
                print("Please open Apple Notes app and try again.")
            raise RuntimeError(error_msg)

        # Log if Notes was launched
        if message == "Notes app launched":
            if self.use_tui and self.console:
                self.console.print("[green]Launched Apple Notes[/green]")
            else:
                logger.info("Launched Apple Notes")
        
        if self.use_tui:
            self._import_with_tui()
        else:
            self._import_classic()
    
    def _import_classic(self):
        """Classic import without TUI."""
        logger.info(f"Starting import from {self.export_dir}")
        logger.info(f"Found {len(self.json_files)} JSON file(s)")

        all_entries = []
        for json_file in self.json_files:
            logger.info(f"Parsing {json_file.name}")
            parser = DayOneParser(json_file)
            entries = parser.parse()
            all_entries.extend(entries)

        # Apply limit if specified
        if self.limit and len(all_entries) > self.limit:
            logger.info(f"Limiting import to {self.limit} entries (total available: {len(all_entries)})")
            all_entries = all_entries[:self.limit]

        self.stats['total_entries'] = len(all_entries)
        logger.info(f"Total entries to import: {len(all_entries)}")
        
        # Process each entry
        for idx, entry in enumerate(all_entries, 1):
            if self.cancelled:
                break
            logger.info(f"Processing entry {idx}/{len(all_entries)}")
            self._import_entry(entry)
        
        # Print summary
        self._print_summary()
    
    def _import_with_tui(self):
        """Import with rich TUI progress display."""
        self.console.print(f"\n[bold blue]Starting import from {self.export_dir}[/bold blue]")
        self.console.print(f"Found {len(self.json_files)} JSON file(s) to process\n")
        
        # Parse all files first
        all_entries = []
        file_entries_map = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            parse_task = progress.add_task("Parsing JSON files...", total=len(self.json_files))
            
            for json_file in self.json_files:
                if self.cancelled:
                    break
                progress.update(parse_task, description=f"Parsing {json_file.name}...")
                try:
                    parser = DayOneParser(json_file)
                    entries = parser.parse()
                    all_entries.extend(entries)
                    file_entries_map[json_file] = len(entries)
                    if self.verbose:
                        self.console.print(f"  [green]✓[/green] {json_file.name}: {len(entries)} entries")
                except Exception as e:
                    self.console.print(f"  [red]✗[/red] Error parsing {json_file.name}: {e}")
                progress.advance(parse_task)
        
        if self.cancelled:
            self.console.print("\n[yellow]Import cancelled by user[/yellow]")
            return

        # Apply limit if specified
        if self.limit and len(all_entries) > self.limit:
            self.console.print(f"[yellow]Limiting import to {self.limit} entries (total available: {len(all_entries)})[/yellow]")
            all_entries = all_entries[:self.limit]

        self.stats['total_entries'] = len(all_entries)
        self.console.print(f"\n[bold]Total entries to import: {len(all_entries)}[/bold]\n")
        
        # Import entries with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            import_task = progress.add_task(
                "[cyan]Importing entries...",
                total=len(all_entries)
            )
            
            current_entry_info = {"text": "", "file": ""}
            
            for idx, entry in enumerate(all_entries, 1):
                if self.cancelled:
                    break
                
                # Update progress description with current entry info
                data = DayOneParser.get_entry_data(entry)
                title = self._extract_title_from_text(data['text'])
                current_file = next((f.name for f in self.json_files if f in file_entries_map), "unknown")
                
                progress.update(
                    import_task,
                    description=f"[cyan]Importing entry {idx}/{len(all_entries)}: {title[:40]}...[/cyan]",
                    advance=1
                )
                
                if self.verbose:
                    self.console.print(f"  Entry {idx}: {title[:50]} ({current_file})")
                
                try:
                    self._import_entry(entry)
                    if self.verbose and self.stats['successful'] % 10 == 0:
                        self.console.print(f"  [green]Progress: {self.stats['successful']} successful, {self.stats['failed']} failed[/green]")
                except KeyboardInterrupt:
                    self.cancelled = True
                    break
                except Exception as e:
                    if self.verbose:
                        self.console.print(f"  [red]Error: {e}[/red]")
        
        # Print summary
        self._print_summary_tui()
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract title from text for display."""
        lines = text.strip().split('\n')
        if lines:
            title = lines[0].strip()
            if len(title) > 50:
                title = title[:47] + '...'
            return title if title else "Untitled Note"
        return "Untitled Note"
    
    def _import_entry(self, entry: Dict):
        """Import a single entry."""
        try:
            # get_entry_data is a static method that just extracts data from the entry dict
            data = DayOneParser.get_entry_data(entry)
            
            # Resolve media files
            photo_paths = []
            for photo in data['photos']:
                path = self.resolver.resolve_photo(photo)
                if path:
                    photo_paths.append(path)
                else:
                    identifier = photo.get('identifier', 'unknown')
                    self.stats['missing_media'].append(f"Photo: {identifier}")
                    logger.warning(f"Could not resolve photo: {identifier}")
            
            video_paths = []
            for video in data['videos']:
                path = self.resolver.resolve_video(video)
                if path:
                    video_paths.append(path)
                else:
                    identifier = video.get('identifier', 'unknown')
                    self.stats['missing_media'].append(f"Video: {identifier}")
                    logger.warning(f"Could not resolve video: {identifier}")
            
            # Create note
            success, _ = self.notes_creator.create_note(
                text=data['text'],
                photos=photo_paths,
                videos=video_paths,
                tags=data['tags'],
                creation_date=data['creationDate'],
                entry_uuid=data['uuid']
            )
            
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
                logger.error(f"Failed to import entry {data['uuid']}")
        
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"Error importing entry: {e}", exc_info=self.verbose)
    
    def _print_summary(self):
        """Print import summary (classic mode)."""
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Total entries processed: {self.stats['total_entries']}")
        print(f"Successful imports: {self.stats['successful']}")
        print(f"Failed imports: {self.stats['failed']}")
        if self.stats['missing_media']:
            print(f"\nMissing media files: {len(self.stats['missing_media'])}")
            if self.verbose:
                for media in self.stats['missing_media'][:10]:  # Show first 10
                    print(f"  - {media}")
                if len(self.stats['missing_media']) > 10:
                    print(f"  ... and {len(self.stats['missing_media']) - 10} more")
        print("="*60)
    
    def _print_summary_tui(self):
        """Print import summary with rich TUI."""
        table = Table(title="Import Summary", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Total entries processed", str(self.stats['total_entries']))
        table.add_row("Successful imports", f"[green]{self.stats['successful']}[/green]")
        table.add_row("Failed imports", f"[red]{self.stats['failed']}[/red]")
        
        if self.stats['missing_media']:
            table.add_row("Missing media files", f"[yellow]{len(self.stats['missing_media'])}[/yellow]")
        
        self.console.print("\n")
        self.console.print(table)
        
        if self.stats['missing_media'] and self.verbose:
            self.console.print("\n[bold yellow]Missing Media Files:[/bold yellow]")
            for media in self.stats['missing_media'][:20]:
                self.console.print(f"  • {media}")
            if len(self.stats['missing_media']) > 20:
                self.console.print(f"  ... and {len(self.stats['missing_media']) - 20} more")
        
        if self.cancelled:
            self.console.print("\n[yellow]⚠ Import was cancelled[/yellow]")
        else:
            self.console.print("\n[bold green]✓ Import completed![/bold green]")


def select_files_tui(export_dir: Path) -> List[Path]:
    """Interactive TUI for selecting JSON files to import."""
    console = Console()
    
    json_files = sorted(list(export_dir.glob('*.json')))
    if not json_files:
        console.print("[red]No JSON files found![/red]")
        return []
    
    # Show file selection interface
    console.print("\n[bold blue]Select JSON files to import:[/bold blue]\n")
    
    selected_indices: Set[int] = set()  # No files selected by default
    
    # Display files with selection status
    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    table.add_column("#", width=4, justify="right", style="dim")
    table.add_column("", width=3)
    table.add_column("File Name", style="cyan")
    table.add_column("Size", justify="right", style="yellow")
    
    for idx, json_file in enumerate(json_files):
        row_num = str(idx + 1)  # 1-based numbering for user
        status = "[green]✓[/green]" if idx in selected_indices else "[dim] [/dim]"
        try:
            size = json_file.stat().st_size
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
        except:
            size_str = "?"
        table.add_row(row_num, status, json_file.name, size_str)
    
    console.print(table)
    console.print("\n[dim]Type numbers to select files (e.g., '1 3 5' to select files 1, 3, and 5), then press Enter to continue[/dim]")
    
    # Allow user to toggle selections
    while True:
        try:
            user_input = Prompt.ask("\n[bold]Selection[/bold] (Enter to confirm, numbers to select/toggle)", default="")
            
            if not user_input.strip():
                # User confirmed, return selected files
                selected = [json_files[i] for i in selected_indices]
                if not selected:
                    console.print("[red]No files selected![/red]")
                    continue
                console.print(f"\n[green]Selected {len(selected)} file(s) for import[/green]\n")
                return selected
            
            # Parse numbers and toggle selection
            try:
                indices = [int(x.strip()) - 1 for x in user_input.split() if x.strip().isdigit()]
                for idx in indices:
                    if 0 <= idx < len(json_files):
                        if idx in selected_indices:
                            selected_indices.remove(idx)
                        else:
                            selected_indices.add(idx)
                
                # Redraw table
                console.clear()
                console.print("\n[bold blue]Select JSON files to import:[/bold blue]\n")
                table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
                table.add_column("#", width=4, justify="right", style="dim")
                table.add_column("", width=3)
                table.add_column("File Name", style="cyan")
                table.add_column("Size", justify="right", style="yellow")
                
                for idx, json_file in enumerate(json_files):
                    row_num = str(idx + 1)  # 1-based numbering for user
                    status = "[green]✓[/green]" if idx in selected_indices else "[dim] [/dim]"
                    try:
                        size = json_file.stat().st_size
                        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
                    except:
                        size_str = "?"
                    table.add_row(row_num, status, json_file.name, size_str)
                
                console.print(table)
                console.print("\n[dim]Type numbers to select files (e.g., '1 3 5' to toggle files 1, 3, and 5), then press Enter to continue[/dim]")
            except ValueError:
                console.print("[red]Invalid input. Please enter numbers separated by spaces.[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Selection cancelled[/yellow]")
            raise SystemExit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Import Day One journal entries into Apple Notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Import with TUI (interactive file selection)
  %(prog)s /path/to/dayone/export

  # Import to specific folder (creates if needed)
  %(prog)s /path/to/dayone/export --folder "Day One Import"

  # Dry run to test without creating notes
  %(prog)s /path/to/dayone/export --dry-run

  # Verbose output
  %(prog)s /path/to/dayone/export --verbose

  # Disable TUI (classic mode)
  %(prog)s /path/to/dayone/export --no-tui
        '''
    )
    
    parser.add_argument(
        'export_dir',
        type=str,
        help='Path to Day One export directory (contains JSON files and photos/videos folders)'
    )
    
    parser.add_argument(
        '--folder', '-f',
        type=str,
        default=None,
        help='Target folder name in Apple Notes (created if it doesn\'t exist)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without actually creating notes'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-tui',
        action='store_true',
        help='Disable TUI and use classic mode'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Maximum number of entries to import (useful for testing)'
    )

    args = parser.parse_args()
    
    # Setup cancellation handler (only for import process, not for prompts)
    cancelled = {'value': False}
    
    def signal_handler(sig, frame):
        cancelled['value'] = True
        # Don't print here - let the import process handle it
    
    try:
        export_dir = Path(args.export_dir)
        if not export_dir.exists():
            print(f"Error: Export directory not found: {export_dir}")
            sys.exit(1)
        
        selected_files = None
        use_tui = not args.no_tui and RICH_AVAILABLE
        
        # File selection TUI (no signal handler during prompts)
        if use_tui:
            console = Console()
            json_files = list(export_dir.glob('*.json'))
            if not json_files:
                console.print(f"[red]No JSON files found in {export_dir}[/red]")
                sys.exit(1)
            
            if len(json_files) > 1:
                try:
                    selected_files = select_files_tui(export_dir)
                    if not selected_files:
                        console.print("[yellow]No files selected. Exiting.[/yellow]")
                        sys.exit(0)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as e:
                    console.print(f"[red]Error during file selection: {e}[/red]")
                    sys.exit(1)
            else:
                # Only one file, skip selection
                selected_files = json_files
                console.print(f"[green]Found 1 JSON file: {json_files[0].name}[/green]\n")
        
        # Folder selection if not provided
        if use_tui and not args.folder:
            console = Console()
            try:
                folder_name = Prompt.ask(
                    "[bold]Apple Notes folder name[/bold] (Enter for default folder)",
                    default=""
                )
                if not folder_name.strip():
                    folder_name = None
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Cancelled[/yellow]")
                sys.exit(0)
        else:
            folder_name = args.folder
        
        # Now set up signal handler for the import process
        signal.signal(signal.SIGINT, signal_handler)
        
        importer = DayOneImporter(
            export_dir=export_dir,
            folder_name=folder_name,
            dry_run=args.dry_run,
            verbose=args.verbose,
            selected_files=selected_files,
            use_tui=use_tui,
            limit=args.limit
        )
        
        # Set cancellation flag
        importer.cancelled = cancelled['value']
        
        importer.import_all()
    
    except (KeyboardInterrupt, SystemExit):
        # SystemExit is raised by select_files_tui when cancelled
        # Re-raise SystemExit to exit cleanly
        if isinstance(sys.exc_info()[1], SystemExit):
            raise
        # Otherwise it's a KeyboardInterrupt
        if RICH_AVAILABLE:
            try:
                console = Console()
                console.print("\n[yellow]Import interrupted by user[/yellow]")
            except:
                print("\nImport interrupted by user")
        else:
            print("\nImport interrupted by user")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"[red]Fatal error: {e}[/red]")
        else:
            logger.error(f"Fatal error: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()
