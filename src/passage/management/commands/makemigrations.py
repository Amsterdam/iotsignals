import logging

from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as MigrateCommand

logger = logging.getLogger(__name__)


class Command(MigrateCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='To ensure you know what you are doing, read docs/.',
        )
        super().add_arguments(parser)

    def handle(self, *app_labels, **options):
        if not options.pop('force', False):
            raise CommandError(
                "The IOTsignals database is about 1TB in size. During a seemingly "
                "harmless migration it could double in size. That will cause a lot "
                "of harm to other production workloads. Make sure to read the docs "
                "at docs/migrations.md. If you know what you are doing, use --force "
                "to create this migration"
            )

        super().handle(*app_labels, **options)
