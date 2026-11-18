"""Package `inventaris`: pengolahan data inventaris laboratorium komputer.

Alur dependensi antar-module (satu arah, tanpa sirkular):

    cli  ->  io_utils  ->  validators  ->  exceptions
     |           |
     |           +------> exceptions
     +--> analysis
     +--> report
"""

__version__ = "1.0.0"
