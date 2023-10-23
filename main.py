from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Path
from pydantic import BaseModel
import csv
from typing import Optional, List
import os
import shutil
from PIL import Image, ImageEnhance, ImageOps
import pytesseract
import spacy
from fastapi.staticfiles import StaticFiles
from io import BytesIO
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

class CalculationRequest(BaseModel):
    pokemon: str
    nature: str
    subskills: list[str]

class CalculationResponse(BaseModel):
    score: int
    grade: str
    percentile: str
    detail: str


# Directorio para cargar las imágenes
upload_dir = "uploaded_images"

# Cargar el modelo de spaCy en español
nlp = spacy.load("es_core_news_sm")


class CalculationRequest(BaseModel):
    pokemon: str
    nature: str
    subskills: List[str]



PTYPE = {
    'Berry': 0,
    'Ingredient': 1,
    'Skill': 2
}

Poke2Type = {
    'Bulbasaur': 'Ingredient', 'Ivysaur': 'Ingredient', 'Venusaur': 'Ingredient',
    'Charmander': 'Ingredient', 'Charmeleon': 'Ingredient', 'Charizard': 'Ingredient',
    'Squirtle': 'Ingredient', 'Wartortle': 'Ingredient', 'Blastoise': 'Ingredient',
    'Caterpie': 'Berry', 'Metapod': 'Berry', 'Butterfree': 'Berry',
    'Rattata': 'Berry', 'Raticate': 'Berry',
    'Ekans': 'Berry', 'Arbok': 'Berry',
    'Pikachu': 'Berry', 'Raichu': 'Berry',
    'Jigglypuff': 'Skill', 'Wigglytuff': 'Skill',
    'Diglett': 'Ingredient', 'Dugtrio': 'Ingredient',
    'Meowth': 'Skill', 'Persian': 'Skill',
    'Psyduck': 'Skill', 'Golduck': 'Skill',
    'Mankey': 'Berry', 'Primeape': 'Berry',
    'Growlithe': 'Skill', 'Arcanine': 'Skill',
    'Bellsprout': 'Ingredient', 'Weepinbell': 'Ingredient', 'Victreebel': 'Ingredient',
    'Geodude': 'Ingredient', 'Graveler': 'Ingredient', 'Golem': 'Ingredient',
    'Slowpoke': 'Skill', 'Slowbro': 'Skill',
    'Magnemite': 'Skill', 'Magneton': 'Skill',
    'Doduo': 'Berry', 'Dodrio': 'Berry',
    'Gastly': 'Ingredient', 'Haunter': 'Ingredient', 'Gengar': 'Ingredient',
    'Cubone': 'Berry', 'Marowak': 'Berry',
    'Kangaskhan': 'Ingredient',
    'Pinsir': 'Ingredient',
    'Ditto': 'Ingredient',
    'Eevee': 'Skill', 'Vaporeon': 'Skill', 'Jolteon': 'Skill', 'Flareon': 'Skill',
    'Chikorita': 'Berry', 'Bayleef': 'Berry', 'Meganium': 'Berry',
    'Cyndaquil': 'Berry', 'Quilava': 'Berry', 'Typhlosion': 'Berry',
    'Totodile': 'Berry', 'Croconaw': 'Berry', 'Feraligatr': 'Berry',
    'Pichu': 'Berry',
    'Igglybuff': 'Skill',
    'Togepi': 'Skill', 'Togetic': 'Skill',
    'Mareep': 'Skill', 'Flaaffy': 'Skill', 'Ampharos': 'Skill',
    'Sudowoodo': 'Skill',
    'Espeon': 'Skill', 'Umbreon': 'Skill',
    'Slowking': 'Skill',
    'Wobbuffet': 'Skill',
    'Heracross': 'Skill',
    'Houndour': 'Berry', 'Houndoom': 'Berry',
    'Larvitar': 'Ingredient', 'Pupitar': 'Ingredient', 'Tyranitar': 'Ingredient',
    'Slakoth': 'Berry', 'Vigoroth': 'Berry', 'Slaking': 'Berry',
    'Sableye': 'Skill',
    'Gulpin': 'Skill', 'Swalot': 'Skill',
    'Swablu': 'Berry', 'Altaria': 'Berry',
    'Absol': 'Ingredient',
    'Wynaut': 'Skill',
    'Spheal': 'Berry', 'Sealeo': 'Berry', 'Walrein': 'Berry',
    'Bonsly': 'Skill',
    'Riolu': 'Skill', 'Lucario': 'Skill',
    'Croagunk': 'Ingredient', 'Toxicroak': 'Ingredient',
    'Magnezone': 'Skill',
    'Togekiss': 'Skill',
    'Leafeon': 'Skill', 'Glaceon': 'Skill', 'Sylveon': 'Skill',
    'Mime Jr.': 'Ingredient', 'Mr. Mime': 'Ingredient',
    'Cleffa': 'Berry', 'Clefairy': 'Berry', 'Clefable': 'Berry'
}

Nature2Score = {
    'Hardy': [1.00, 1.00, 1.00], 'Lonely': [1.00, 1.00, 0.67], 'Brave': [1.67, 1.67, 1.67],
    'Adamant': [3.00, -0.17, 0.67], 'Naughty': [1.83, 1.67, -0.17],
    'Bold': [-1.33, -1.33, -1.00], 'Docile': [1.00, 1.00, 1.00], 'Relaxed': [-0.67, -0.67, -0.33],
    'Impish': [1.50, -1.33, -0.17], 'Lax': [0.17, 0.17, -1.00],
    'Timid': [-1.00, -1.00, -1.00], 'Hasty': [0.33, 0.33, 0], 'Serious': [1.00, 1.00, 1.00],
    'Jolly': [2.17, -1.00, 0.17], 'Naive': [0.83, 0.58, -1.00],
    'Modest': [-1.67, 0.50, -0.33], 'Mild': [-1.00, 1.17, 0], 'Quiet': [-0.67, 2.00, 1.00],
    'Bashful': [1.00, 1.00, 1.00], 'Rash': [-0.50, 2.00, -0.67],
    'Calm': [-0.67, -0.67, 0.67], 'Gentle': [-0.33, 0.33, 1.33], 'Sassy': [0, 0.25, 1.67],
    'Careful': [1.50, -1.00, 1.33], 'Quirky': [1.00, 1.00, 1.00]
    }

Subskill2Score = {
    "Berry Finding S": [5, 4, 5],
    "Dream Shard Bonus": [2, 2, 2],
    "Energy Recovery Bonus": [3, 3, 3],
    "Helping Bonus": [5, 5, 5],
    "Helping Speed S": [3, 3, 3],
    "Helping Speed M": [4, 4, 4],
    "Ingredient Finder S": [1, 4, 3],
    "Ingredient Finder M": [1, 5, 4],
    "Inventory Up S": [2, 3, 2],
    "Inventory Up M": [3, 4, 3],
    "Inventory Up L": [4, 5, 4],
    "Research EXP Bonus": [2, 2, 2],
    "Skill Level Up S": [3, 3, 4],
    "Skill Level Up M": [4, 4, 5],
    "Skill Trigger S": [3, 3, 4],
    "Skill Trigger M": [4, 4, 5],
    "Sleep EXP Bonus": [3, 3, 3]
}

LevelScaling = [1.5, 1.25, 1, 0.75, 0.5]

PercentileBerry = [ 9.58, 10.25, 10.67, 11.  , 11.25, 11.5 , 11.75, 11.83, 12.  ,
    12.25, 12.33, 12.5 , 12.58, 12.75, 12.83, 13.  , 13.08, 13.25,
    13.25, 13.42, 13.5 , 13.58, 13.75, 13.75, 13.83, 14.  , 14.  ,
    14.08, 14.25, 14.25, 14.33, 14.5 , 14.5 , 14.58, 14.67, 14.75,
    14.83, 14.92, 15.  , 15.  , 15.08, 15.25, 15.25, 15.33, 15.42,
    15.5 , 15.5 , 15.58, 15.75, 15.75, 15.83, 15.92, 16.  , 16.  ,
    16.08, 16.25, 16.25, 16.33, 16.42, 16.5 , 16.5 , 16.58, 16.75,
    16.75, 16.83, 16.92, 17.  , 17.  , 17.17, 17.25, 17.25, 17.42,
    17.5 , 17.5 , 17.67, 17.75, 17.75, 17.92, 18.  , 18.08, 18.25,
    18.25, 18.42, 18.5 , 18.58, 18.75, 18.83, 19.  , 19.08, 19.25,
    19.42, 19.58, 19.75, 20.  , 20.25, 20.5 , 20.75, 21.17, 21.75,
    25.75]
PercentileIngredient = [13.42, 13.92, 14.25, 14.5 , 14.75, 14.92, 15.08, 15.25, 15.33,
    15.5 , 15.58, 15.75, 15.83, 15.92, 16.  , 16.08, 16.25, 16.25,
    16.33, 16.5 , 16.5 , 16.58, 16.67, 16.75, 16.83, 16.92, 17.  ,
    17.  , 17.08, 17.17, 17.25, 17.25, 17.33, 17.42, 17.5 , 17.5 ,
    17.58, 17.67, 17.75, 17.75, 17.83, 17.92, 17.92, 18.  , 18.  ,
    18.08, 18.17, 18.25, 18.25, 18.33, 18.42, 18.5 , 18.5 , 18.5 ,
    18.58, 18.67, 18.75, 18.75, 18.83, 18.92, 19.  , 19.  , 19.08,
    19.17, 19.25, 19.25, 19.25, 19.42, 19.5 , 19.5 , 19.58, 19.67,
    19.75, 19.75, 19.83, 19.92, 20.  , 20.  , 20.08, 20.25, 20.25,
    20.33, 20.5 , 20.5 , 20.67, 20.75, 20.75, 20.92, 21.  , 21.17,
    21.25, 21.42, 21.5 , 21.75, 21.92, 22.08, 22.25, 22.67, 23.17,
    25.75]

PercentileSkill = [13.0 , 13.5 , 13.92, 14.25, 14.42, 14.58, 14.75, 15.  , 15.08,
        15.25, 15.33, 15.5 , 15.58, 15.75, 15.75, 15.92, 16.  , 16.08,
        16.17, 16.25, 16.33, 16.42, 16.5 , 16.58, 16.67, 16.75, 16.75,
        16.92, 17.  , 17.  , 17.08, 17.17, 17.25, 17.25, 17.33, 17.42,
        17.5 , 17.5 , 17.58, 17.67, 17.75, 17.75, 17.92, 17.92, 18.  ,
        18.  , 18.08, 18.17, 18.25, 18.25, 18.33, 18.42, 18.5 , 18.5 ,
        18.58, 18.67, 18.75, 18.75, 18.83, 18.92, 19.  , 19.  , 19.08,
        19.17, 19.25, 19.25, 19.33, 19.42, 19.5 , 19.58, 19.67, 19.75,
        19.75, 19.83, 19.92, 20.  , 20.08, 20.17, 20.25, 20.25, 20.42,
        20.5 , 20.58, 20.67, 20.75, 20.92, 21.  , 21.08, 21.17, 21.33,
        21.42, 21.58, 21.75, 21.92, 22.08, 22.33, 22.58, 22.92, 23.42,
        26.17]

Score2Grade = [
    [25, "F"],
    [50, "D"],
    [70, "C"],
    [85, "B"],
    [95, "A"],
    [100, "S"]
]

@app.post("/procesar-imagen-y-valorar-pokemon/", summary="Endpoint valorar pokemon de pokemon sleep")
async def process_image(file: UploadFile):
    """
    # Endpoint para procesar el texto de una captura del juego pokemon sleep y con la informacion generada valorar el pokemon de la captura
    ## Status Code
    * 200 OK: Si el análisis se realiza exitosamente.
    * 400 Bad Request: Si el texto de la captura no es válido o no se puede analizar.
    * 500 Internal Server Error: En caso de un error interno del servidor.

    """
    try:
        # Crear el directorio de carga si no existe
        os.makedirs(upload_dir, exist_ok=True)

        # Guardar la imagen cargada en el directorio de carga
        image_path = os.path.join(upload_dir, file.filename)
        with open(image_path, "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)

        # Abre la imagen
        image = Image.open(image_path)
        factor_de_brillo = 0.5  # Valores menores oscurecen la imagen
        factor_de_contraste = 10.0  # Valores mayores aumentan el contraste

        # Aplica el ajuste de brillo y contraste
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(factor_de_brillo)

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor_de_contraste)


        # Define las coordenadas en porcentajes para cada sección en relación con el ancho y alto de la imagen
        pokemon_section_coords = (0.29, 0.1, 0.56, 0.12)
        natures_section_coords = (0.1, 0.65, 0.45, 0.68)
        subskill1_coords = (0.08, 0.34, 0.47, 0.37)
        subskill2_coords = (0.53, 0.34, 0.92, 0.37)
        subskill3_coords = (0.08, 0.41, 0.47, 0.44)
        subskill4_coords = (0.53, 0.41, 0.92, 0.44)
        subskill5_coords = (0.08, 0.48, 0.47, 0.51)

        # Calcula las coordenadas en píxeles en función de las proporciones y el tamaño de la imagen
        image_width, image_height = image.size
        pokemon_section_coords = (
            int(pokemon_section_coords[0] * image_width),
            int(pokemon_section_coords[1] * image_height),
            int(pokemon_section_coords[2] * image_width),
            int(pokemon_section_coords[3] * image_height)
        )
        natures_section_coords = (
            int(natures_section_coords[0] * image_width),
            int(natures_section_coords[1] * image_height),
            int(natures_section_coords[2] * image_width),
            int(natures_section_coords[3] * image_height)
        )
        subskill1_coords = (
            int(subskill1_coords[0] * image_width),
            int(subskill1_coords[1] * image_height),
            int(subskill1_coords[2] * image_width),
            int(subskill1_coords[3] * image_height)
        )
        subskill2_coords = (
            int(subskill2_coords[0] * image_width),
            int(subskill2_coords[1] * image_height),
            int(subskill2_coords[2] * image_width),
            int(subskill2_coords[3] * image_height)
        )
        subskill3_coords = (
            int(subskill3_coords[0] * image_width),
            int(subskill3_coords[1] * image_height),
            int(subskill3_coords[2] * image_width),
            int(subskill3_coords[3] * image_height)
        )
        subskill4_coords = (
            int(subskill4_coords[0] * image_width),
            int(subskill4_coords[1] * image_height),
            int(subskill4_coords[2] * image_width),
            int(subskill4_coords[3] * image_height)
        )
        subskill5_coords = (
            int(subskill5_coords[0] * image_width),
            int(subskill5_coords[1] * image_height),
            int(subskill5_coords[2] * image_width),
            int(subskill5_coords[3] * image_height)
        )

        # Recorta las secciones
        pokemon_section = image.crop(pokemon_section_coords)
        natures_section = image.crop(natures_section_coords)
        subskill1 = image.crop(subskill1_coords)
        subskill2 = image.crop(subskill2_coords)
        subskill3 = image.crop(subskill3_coords)
        subskill4 = image.crop(subskill4_coords)
        subskill5 = image.crop(subskill5_coords)

        # Guarda las secciones recortadas
        pokemon_section.save(os.path.join(upload_dir, "pokemon_section.png"))
        natures_section.save(os.path.join(upload_dir, "natures_section.png"))
        subskill1.save(os.path.join(upload_dir, "subskill1.png"))
        subskill2.save(os.path.join(upload_dir, "subskill2.png"))
        subskill3.save(os.path.join(upload_dir, "subskill3.png"))
        subskill4.save(os.path.join(upload_dir, "subskill4.png"))
        subskill5.save(os.path.join(upload_dir, "subskill5.png"))

        # Obtener el texto de las secciones recortadas
        pokemon_text = pytesseract.image_to_string(pokemon_section)
        natures_text = pytesseract.image_to_string(natures_section)
        subskill1_text = pytesseract.image_to_string(subskill1)
        subskill2_text = pytesseract.image_to_string(subskill2)
        subskill3_text = pytesseract.image_to_string(subskill3)
        subskill4_text = pytesseract.image_to_string(subskill4)
        subskill5_text = pytesseract.image_to_string(subskill5)

        # Inicializa el diccionario de resultados
        result = {
            "text_info": {}  # Inicializa el diccionario de información de texto
        }
        # Verificar si la información es válida
        if not pokemon_text or not natures_text or not subskill1_text or not subskill2_text or not subskill3_text or not subskill4_text or not subskill5_text:
            raise HTTPException(status_code=400, detail="Imagen de captura no contiene información necesaria")

        # Después de procesar el texto de cada sección, guárdalo en el diccionario de información de texto
        result["text_info"] = {
            "pokemon": pokemon_text,
            "natures": natures_text,
            "subskill1": subskill1_text,
            "subskill2": subskill2_text,
            "subskill3": subskill3_text,
            "subskill4": subskill4_text,
            "subskill5": subskill5_text
        }

        # Crear un diccionario result con la información de texto
        result = {
            "pokemon": pokemon_text.strip(),
            "nature": natures_text.strip(),
            "subskills": [
                subskill1_text.strip(),
                subskill2_text.strip(),
                subskill3_text.strip(),
                subskill4_text.strip(),
                subskill5_text.strip()
            ]
        }

        # Asignar los valores a las variables
        pokemon = result["pokemon"]
        nature = result["nature"]
        subskills = result["subskills"]

        idx = PTYPE[Poke2Type[pokemon]]
        explain_str = "Score in detail: "

        score_nature = Nature2Score[nature][idx]
        explain_str += "[Nature] " + str(score_nature)
        score_subskill = 0
        
        # Obtener puntaje de las subhabilidades
        explain_str += " + [Subskill] "
        for ii in range(5):
            iv = subskills[ii]
            sii = Subskill2Score[iv][idx] * LevelScaling[ii]
            score_subskill += sii
            explain_str += str(sii)
            if ii != 4:
                explain_str += " + "
        total_score = score_nature + score_subskill

        # Calcular porcentaje
        if idx == 0:
            percentile_cache = PercentileBerry
        elif idx == 1:
            percentile_cache = PercentileIngredient
        else:
            percentile_cache = PercentileSkill
            
        pct_ii = None
        for i, x in enumerate(percentile_cache):
            if x >= total_score:
                pct_ii = i
                break

        # Obtener la clasificación (grade)
        grade_idx = next((i for i, x in enumerate(Score2Grade) if pct_ii <= x[0]), None)
        grade = Score2Grade[grade_idx][1]

        print(total_score)
        print(grade)
    
        result = {
            "score": total_score,
            "grade": grade,
            "percentile": f"{pct_ii}/100",
            "detail": explain_str,
            "pokemon": pokemon,
            "nature": nature,
            "subskills": subskills
            
            
            
        }

        return result
    except Exception as e:
         raise HTTPException(status_code=500, detail="Error al procesar la imagen y generar un resultado")
