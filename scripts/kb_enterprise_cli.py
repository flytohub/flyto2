#!/usr/bin/env python3
"""
Enterprise Knowledge Base CLI

Enterprise-grade command-line interface for knowledge base management.

Features:
- Ingest documents with version control
- View audit logs
- Check quality metrics
- Rollback operations
- Statistics and monitoring
- Multi-language support (English + 中文)
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.knowledge.enterprise_kb_manager import EnterpriseKBManager, OperationType


def print_banner():
    """Print enterprise banner"""
    print()
    print("=" * 80)
    print(" " * 20 + "🏢 Enterprise Knowledge Base Manager")
    print(" " * 25 + "Version 1.0.0 (Enterprise)")
    print("=" * 80)
    print()


async def cmd_ingest(args):
    """Ingest documents"""
    manager = EnterpriseKBManager(
        enable_translation=not args.no_translate,
        translation_provider=args.translator
    )

    documents = []
    if args.document:
        # Single document
        doc_path = Path(args.document)
        if not doc_path.exists():
            print(f"❌ Error: Document not found: {doc_path}")
            return 1
        documents = [doc_path]
    else:
        # Default: All implementation guides
        documents = [
            manager.project_root / "IMPLEMENTATION_GUIDE_V4.md",
            manager.project_root / "IMPLEMENTATION_GUIDE_V4_CRITICAL_SUPPLEMENTS.md"
        ]

    result = await manager.ingest_all_enterprise(
        documents=documents,
        force=args.force,
        user=args.user
    )

    if result["success"]:
        print(f"\n✅ Success: {result['total_chunks']} chunks ingested")
        return 0
    else:
        print(f"\n❌ Failed: {result['total_errors']} errors occurred")
        return 1


def cmd_history(args):
    """Show document version history"""
    manager = EnterpriseKBManager()

    if args.document_id:
        # Show specific document history
        versions = manager.get_document_history(args.document_id)

        if not versions:
            print(f"📄 No history found for document: {args.document_id}")
            return 0

        print(f"\n📄 Version History: {args.document_id}")
        print("=" * 80)

        for v in versions:
            print(f"\n🔖 Version {v.version}")
            print(f"   Timestamp: {v.timestamp}")
            print(f"   Operation: {v.operation.value}")
            print(f"   Hash: {v.hash[:16]}...")
            print(f"   Chunks: {v.chunks_count}")

            if v.metadata.get('quality'):
                q = v.metadata['quality']
                print(f"   Quality:")
                print(f"      - Language: {q['language_detected']}")
                print(f"      - Completeness: {q['completeness_score']:.0%}")
                print(f"      - Readability: {q['readability_score']:.0%}")

    else:
        # Show all documents
        print("\n📚 All Documents")
        print("=" * 80)

        for doc_id, versions in manager.versions.items():
            latest = versions[-1]
            print(f"\n📄 {doc_id}")
            print(f"   Current version: {latest.version}")
            print(f"   Last updated: {latest.timestamp}")
            print(f"   Chunks: {latest.chunks_count}")
            print(f"   Operation: {latest.operation.value}")

    return 0


def cmd_audit(args):
    """Show audit logs"""
    manager = EnterpriseKBManager()

    logs = manager.get_audit_logs(limit=args.limit)

    if not logs:
        print("📋 No audit logs found")
        return 0

    print(f"\n📋 Audit Logs (Last {len(logs)})")
    print("=" * 80)

    for log in logs:
        status = "✅" if log.success else "❌"
        print(f"\n{status} {log.timestamp}")
        print(f"   Operation: {log.operation if isinstance(log.operation, str) else log.operation.value}")
        print(f"   User: {log.user}")
        print(f"   Document: {log.document_id}")
        print(f"   Chunks affected: {log.chunks_affected}")

        if log.error_message:
            print(f"   ❌ Error: {log.error_message}")

        if log.metrics:
            if 'elapsed_seconds' in log.metrics:
                print(f"   Time: {log.metrics['elapsed_seconds']:.2f}s")

            if 'quality' in log.metrics:
                q = log.metrics['quality']
                print(f"   Quality: {q['completeness_score']:.0%} completeness, {q['readability_score']:.0%} readability")

    return 0


def cmd_stats(args):
    """Show statistics"""
    manager = EnterpriseKBManager()

    stats = manager.get_statistics()

    print("\n📊 Knowledge Base Statistics")
    print("=" * 80)
    print(f"\n📚 Documents")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Total versions: {stats['total_versions']}")

    print(f"\n🔍 Vectors")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Vector dimension: {stats['vector_dimension']}")

    if stats['latest_documents']:
        print(f"\n📄 Latest Documents")
        print(f"   {'Document ID':<40} {'Version':<10} {'Chunks':<10} {'Updated'}")
        print("   " + "-" * 80)

        for doc in stats['latest_documents']:
            timestamp = datetime.fromisoformat(doc['timestamp']).strftime('%Y-%m-%d %H:%M')
            print(f"   {doc['doc_id']:<40} {doc['version']:<10} {doc['chunks']:<10} {timestamp}")

    return 0


def cmd_export(args):
    """Export audit logs to file"""
    manager = EnterpriseKBManager()

    logs = manager.get_audit_logs(limit=args.limit)

    output_file = Path(args.output)

    # Prepare export data
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_logs": len(logs),
        "logs": [
            {
                "timestamp": log.timestamp,
                "operation": log.operation.value,
                "user": log.user,
                "document_id": log.document_id,
                "chunks_affected": log.chunks_affected,
                "success": log.success,
                "error_message": log.error_message,
                "metrics": log.metrics
            }
            for log in logs
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(logs)} audit logs to: {output_file}")
    return 0


def main():
    """Main CLI entry point"""
    print_banner()

    parser = argparse.ArgumentParser(
        description='Enterprise Knowledge Base Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all implementation guides
  python scripts/kb_enterprise_cli.py ingest

  # Ingest specific document
  python scripts/kb_enterprise_cli.py ingest --document path/to/doc.md

  # Force re-ingest (ignore hash check)
  python scripts/kb_enterprise_cli.py ingest --force

  # View document history
  python scripts/kb_enterprise_cli.py history --doc IMPLEMENTATION_GUIDE_V4

  # View all documents
  python scripts/kb_enterprise_cli.py history

  # View audit logs
  python scripts/kb_enterprise_cli.py audit --limit 50

  # Show statistics
  python scripts/kb_enterprise_cli.py stats

  # Export audit logs
  python scripts/kb_enterprise_cli.py export --output logs/audit_export.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents into knowledge base')
    ingest_parser.add_argument('--document', '-d', help='Specific document to ingest')
    ingest_parser.add_argument('--force', '-f', action='store_true', help='Force re-ingest even if unchanged')
    ingest_parser.add_argument('--user', '-u', default='system', help='User performing the operation')
    ingest_parser.add_argument('--no-translate', action='store_true', help='Disable translation to English')
    ingest_parser.add_argument('--translator', default='ollama', choices=['ollama', 'openai'], help='Translation provider (default: ollama)')

    # History command
    history_parser = subparsers.add_parser('history', help='Show document version history')
    history_parser.add_argument('--doc', '--document-id', dest='document_id', help='Specific document ID')

    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Show audit logs')
    audit_parser.add_argument('--limit', '-l', type=int, default=50, help='Number of logs to show')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show knowledge base statistics')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export audit logs to file')
    export_parser.add_argument('--output', '-o', default='logs/audit_export.json', help='Output file path')
    export_parser.add_argument('--limit', '-l', type=int, default=1000, help='Number of logs to export')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == 'ingest':
            return asyncio.run(cmd_ingest(args))
        elif args.command == 'history':
            return cmd_history(args)
        elif args.command == 'audit':
            return cmd_audit(args)
        elif args.command == 'stats':
            return cmd_stats(args)
        elif args.command == 'export':
            return cmd_export(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
