<style>
    .stApp > header { display: none !important; }

    .stApp {
        background-color: #007A33;
        color: white;
        font-size: 16px;
    }

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 2rem !important;
        font-weight: 900;
        color: #fff;
        text-align: center;
        padding: 40px 0;
        text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
    }

    .image-grid {
        display: flex;
        justify-content: center;
        gap: 50px;
        padding: 40px;
        flex-wrap: wrap;
    }

    .image-grid img {
        max-width: 600px;
        height: auto;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.6);
        background-color: white;
    }

    .stAlert {
        background-color: #333 !important;
        color: #fff !important;
        border-left: 5px solid #31A354 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #E0E0E0;
        padding: 1rem;
    }

    [data-testid="stSidebar"] * {
        font-size: 20px !important;
        font-weight: 100;
        color: #000 !important;
    }
</style>

<div class="main-title">🌿 Imágenes en Dos Columnas</div>

<div class="image-grid">
    <img src="{{ url_for('static', filename='tu_imagen.png') }}" alt="Imagen 1">
    <img src="{{ url_for('static', filename='tu_imagen.png') }}" alt="Imagen 2">
</div>
