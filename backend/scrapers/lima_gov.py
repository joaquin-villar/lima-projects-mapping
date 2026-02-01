# backend/scrapers/lima_gov.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class LimaProjectScraper:
    """Scraper for Lima government project announcements from news sources"""
    
    # News sources that report on Lima projects
    SOURCES = {
        'infobae': 'https://www.infobae.com/peru/',
        'gob_pe': 'https://www.gob.pe/busquedas?institucion%5B%5D=munilima&term=proyecto+obra',
    }
    
    def extract_districts_from_text(self, text: str) -> List[str]:
        """Extract district names from project text"""
        # Common Lima districts
        districts = [
            'Barranco', 'Cercado de Lima', 'Miraflores', 'San Isidro', 'Surco',
            'La Molina', 'San Borja', 'Lince', 'Jesús María', 'Magdalena',
            'Pueblo Libre', 'San Miguel', 'Breña', 'Rímac', 'Los Olivos',
            'Independencia', 'Comas', 'Carabayllo', 'San Martín de Porres',
            'San Juan de Miraflores', 'Villa María del Triunfo', 'Villa El Salvador',
            'San Juan de Lurigancho', 'Ate', 'Santa Anita', 'El Agustino',
            'La Victoria', 'Surquillo', 'Chorrillos', 'Callao'
        ]
        
        found_districts = []
        text_lower = text.lower()
        
        for district in districts:
            if district.lower() in text_lower:
                found_districts.append(district)
        
        return list(set(found_districts))  # Remove duplicates
    
    def scrape_gob_pe_search(self) -> List[Dict]:
        """
        Scrape project info from gob.pe search results
        This searches for "proyecto obra" in Municipalidad de Lima
        """
        try:
            url = 'https://www.gob.pe/busquedas?contenido%5B%5D=noticias&institucion%5B%5D=munilima&term=obra+proyecto'
            
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code != 200:
                logger.warning(f"gob.pe returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            projects = []
            
            # Find news items (adjust selectors based on actual HTML)
            news_items = soup.select('.list-group-item, .card, article')
            
            for item in news_items[:10]:  # Limit to 10 most recent
                try:
                    # Extract title
                    title_elem = item.select_one('h2, h3, .title, a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract description/summary
                    desc_elem = item.select_one('p, .description, .summary')
                    description = desc_elem.get_text(strip=True) if desc_elem else title
                    
                    # Extract link
                    link_elem = item.select_one('a[href]')
                    source_url = link_elem['href'] if link_elem else url
                    if source_url.startswith('/'):
                        source_url = 'https://www.gob.pe' + source_url
                    
                    # Extract districts from text
                    full_text = f"{title} {description}"
                    districts = self.extract_districts_from_text(full_text)
                    
                    # Only add if it seems to be about infrastructure/projects
                    project_keywords = ['obra', 'proyecto', 'construcción', 'infraestructura', 
                                       'vía', 'parque', 'recuperación', 'mejora']
                    
                    if any(keyword in title.lower() for keyword in project_keywords):
                        project = {
                            'name': title[:200],  # Truncate if too long
                            'description': description[:500],
                            'districts': districts if districts else ['Lima'],  # Default to Lima if none found
                            'status': 'scraped',
                            'source_url': source_url,
                            'scraped_at': datetime.utcnow(),
                            'verified': False
                        }
                        projects.append(project)
                
                except Exception as e:
                    logger.warning(f"Error parsing item: {e}")
                    continue
            
            logger.info(f"Scraped {len(projects)} projects from gob.pe")
            return projects
            
        except Exception as e:
            logger.error(f"Error scraping gob.pe: {e}")
            return []
    
    def scrape_manual_known_projects(self) -> List[Dict]:
        """
        Manually add known major projects from recent news
        This ensures we have some data even if scraping fails
        """
        known_projects = [
            {
                'name': 'Vía Expresa Grau - Conexión Metropolitano con Línea 1',
                'description': 'Corredor de 2.8 km que enlazará el Metropolitano con la Línea 1 del Metro, beneficiando a 2 millones de usuarios. Incluye 4 paraderos: Abancay, Andahuaylas, Parinacochas y Nicolás Ayllón.',
                'districts': ['Cercado de Lima'],
                'status': 'en_construccion',
                'source_url': 'https://www.infobae.com/peru/2025/12/20/asi-sera-la-nueva-megaobra-que-reducira-a-45-minutos-el-viaje-de-norte-a-sur-en-lima-y-unira-8-distritos/',
                'scraped_at': datetime.utcnow(),
                'verified': False
            },
            {
                'name': 'Teleférico Urbano Independencia - San Juan de Miraflores',
                'description': 'Sistema de teleférico para reducir en 2 horas el tiempo de viaje entre el norte y sur de Lima. Inversión de 350 millones de soles.',
                'districts': ['Independencia', 'San Juan de Miraflores'],
                'status': 'planificado',
                'source_url': 'https://www.infobae.com/peru/2023/11/04/cuales-son-los-5-proyectos-de-infraestructura-que-la-municipalidad-de-lima-anuncio-que-priorizara/',
                'scraped_at': datetime.utcnow(),
                'verified': False
            },
            {
                'name': 'Ampliación Norte del Metropolitano',
                'description': 'Extensión del servicio Metropolitano desde Plaza San Miguel hasta Av. Chimpu Ocllo en Carabayllo, recorriendo toda la Av. Universitaria.',
                'districts': ['San Miguel', 'Carabayllo', 'Los Olivos'],
                'status': 'planificado',
                'source_url': 'https://visionminera.com/cuales-son-los-5-proyectos-infraestructura-municipalidad-lima-priorizara.html',
                'scraped_at': datetime.utcnow(),
                'verified': False
            },
            {
                'name': 'Ampliación Sur del Metropolitano',
                'description': 'Nueva ruta del Metropolitano desde Barranco hasta San Juan de Miraflores, cruzando por gran parte de Surco.',
                'districts': ['Barranco', 'Surco', 'San Juan de Miraflores'],
                'status': 'planificado',
                'source_url': 'https://visionminera.com/cuales-son-los-5-proyectos-infraestructura-municipalidad-lima-priorizara.html',
                'scraped_at': datetime.utcnow(),
                'verified': False
            },
            {
                'name': 'Vía Expresa Sur - Obras Complementarias',
                'description': 'Obras complementarias de 5km de vía que conecta Barranco, Surco y San Juan de Miraflores. Incluye conexión con Panamericana Sur y acceso a Mall del Sur.',
                'districts': ['Barranco', 'Surco', 'San Juan de Miraflores'],
                'status': 'en_construccion',
                'source_url': 'https://larepublica.pe/sociedad/2025/12/03/municipalidad-de-lima-declara-en-emergencia-obras-complementarias-en-la-via-expresa-sur-que-inauguro-hace-mas-de-3-meses-44607',
                'scraped_at': datetime.utcnow(),
                'verified': False
            }
        ]
        
        return known_projects
    
    def scrape_all(self) -> List[Dict]:
        """Scrape all sources and combine results"""
        all_projects = []
        
        # Try to scrape live data
        all_projects.extend(self.scrape_gob_pe_search())
        
        # Add known projects as fallback
        all_projects.extend(self.scrape_manual_known_projects())
        
        # Remove duplicates based on name similarity
        unique_projects = self._deduplicate_projects(all_projects)
        
        logger.info(f"Total unique projects scraped: {len(unique_projects)}")
        return unique_projects
    
    def _deduplicate_projects(self, projects: List[Dict]) -> List[Dict]:
        """Remove duplicate projects based on name similarity"""
        if not projects:
            return []
        
        unique = []
        seen_names = set()
        
        for project in projects:
            # Normalize name for comparison
            name_normalized = project['name'].lower().strip()
            name_key = ''.join(name_normalized.split())  # Remove spaces
            
            if name_key not in seen_names:
                unique.append(project)
                seen_names.add(name_key)
        
        return unique