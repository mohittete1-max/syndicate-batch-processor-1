import os
from PIL import Image, ImageOps

def get_player_avatar(name):
    """Loads a real player photo from a local folder if available, else falls back to initials"""
    clean_name = name.replace("*(C)*", "").replace("*(VC)*", "").replace("(C)", "").replace("(VC)", "").strip()
    
    # Check if a local image file exists for this player (e.g., 'roston_chase.png')
    filename = clean_name.lower().replace(" ", "_") + ".png"
    photo_path = os.path.join("player_photos", filename)
    
    try:
        if os.path.exists(photo_path):
            # Load real player image, crop into a square, and make it circular
            avatar_img = Image.open(photo_path).convert("RGBA")
            avatar_img = ImageOps.fit(avatar_img, (128, 128), centering=(0.5, 0.5))
            
            mask = Image.new("L", avatar_img.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse([0, 0, avatar_img.size[0], avatar_img.size[1]], fill=255)
            avatar_img.putalpha(mask)
            return avatar_img
    except Exception:
        pass
        
    # Fallback to default generated badge if the photo file isn't in the folder yet
    fallback = Image.new("RGBA", (128, 128), (30, 41, 59, 255))
    return fallback
