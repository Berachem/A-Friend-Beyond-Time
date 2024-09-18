from PIL import Image

# Met à jour ce chemin avec celui où se trouve ton image
image_path = r"C:\Users\polom\OneDrive\Bureau\gamejam\Game_Jam\assets\images\kenney_roguelike-indoors\Tilesheets\roguelikeIndoor_transparent.png"
spritesheet = Image.open(image_path)

# Taille d'une tuile
tile_width = 16
tile_height = 16

# Marge entre les tuiles
margin = 1

# Fonction pour extraire une tuile selon les coordonnées de la grille
def get_tile(spritesheet, x_index, y_index, tile_width, tile_height, margin):
    # Calculer la position de la tuile dans l'image en tenant compte de la marge
    left = x_index * (tile_width + margin) + margin
    upper = y_index * (tile_height + margin) + margin
    right = left + tile_width
    lower = upper + tile_height

    # Extraire la tuile
    tile = spritesheet.crop((left, upper, right, lower))
    return tile

# Exemple : prendre la tuile à la 3ème colonne et 2ème ligne
x_index = 0  # 3ème colonne (index commence à 0)
y_index = 2  # 2ème ligne (index commence à 0)

# Extraire la tuile
tile = get_tile(spritesheet, x_index, y_index, tile_width, tile_height, margin)

# Sauvegarder ou afficher la tuile extraite
tile.show()  # Afficher la tuile
tile.save("C:/Users/polom/OneDrive/Bureau/gamejam/Game_Jam/selected_tile.png")  # Sauvegarder la tuile dans un fichier
