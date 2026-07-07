# Diretórios / programas de aceleração
from services.scraping.directories.ace_ventures import ingest_article as ingest_ace
from services.scraping.directories.liga_ventures import ingest_article as ingest_liga
from services.scraping.directories.distrito import ingest_article as ingest_distrito
from services.scraping.directories.startupsbr import ingest_article as ingest_startupsbr

# Plataformas de inovação
from services.scraping.directories.startse import ingest_article as ingest_startse
from services.scraping.directories.cubo import ingest_article as ingest_cubo
from services.scraping.directories.abstartups import ingest_article as ingest_abstartups
from services.scraping.directories.endeavor import ingest_article as ingest_endeavor
from services.scraping.directories.latitud import ingest_article as ingest_latitud

# Aceleradoras
from services.scraping.directories.wow import ingest_article as ingest_wow

# Portais de notícias
from services.scraping.directories.brazil_journal import ingest_article as ingest_braziljournal
from services.scraping.directories.neofeed import ingest_article as ingest_neofeed
from services.scraping.directories.exame import ingest_article as ingest_exame
from services.scraping.directories.pegn import ingest_article as ingest_pegn
from services.scraping.directories.mobile_time import ingest_article as ingest_mobiletime
