# MangaNarrator 📚➡️🎬


## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **AI/LLM:** Google Gemini API (`gemini-2.0-flash`)
*   **TTS:** Deepgram API
*   **Video Processing:** FFmpeg
*   **PDF Processing:** PyMuPDF
*   **Frontend:** HTML5, CSS3 (Neurobrutalist Design), Vanilla JS

## 📦 Installation

### Prerequisites
*   Python 3.10+
*   [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH.
*   API Keys for [Google Gemini](https://aistudio.google.com/) and [Deepgram](https://deepgram.com/).

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/MangaNarrator.git
    cd MangaNarrator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your keys:
    ```ini
    GOOGLE_API_KEY=your_gemini_api_key_here
    DEEPGRAM_API_KEY=your_deepgram_api_key_here
    SECRET_KEY=your_flask_secret_key
    ```

## 🏃‍♂️ Usage

1.  **Start the Backend Server:**
    ```bash
    cd backend
    python server.py
    ```
    The server will start at `http://127.0.0.1:5000`.

2.  **Open the App:**
    Go to `http://127.0.0.1:5000` in your browser.

3.  **Generate a Video:**
# MangaNarrator 📚➡️🎬


## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **AI/LLM:** Google Gemini API (`gemini-2.0-flash`)
*   **TTS:** Deepgram API
*   **Video Processing:** FFmpeg
*   **PDF Processing:** PyMuPDF
*   **Frontend:** HTML5, CSS3 (Neurobrutalist Design), Vanilla JS

## 📦 Installation

### Prerequisites
*   Python 3.10+
*   [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH.
*   API Keys for [Google Gemini](https://aistudio.google.com/) and [Deepgram](https://deepgram.com/).

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/MangaNarrator.git
    cd MangaNarrator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your keys:
    ```ini
    GOOGLE_API_KEY=your_gemini_api_key_here
    DEEPGRAM_API_KEY=your_deepgram_api_key_here
    SECRET_KEY=your_flask_secret_key
    ```

## 🏃‍♂️ Usage

1.  **Start the Backend Server:**
    ```bash
    cd backend
    python server.py
    ```
    The server will start at `http://127.0.0.1:5000`.

2.  **Open the App:**
    Go to `http://127.0.0.1:5000` in your browser.

3.  **Generate a Video:**
    *   Upload a Manga PDF file.
    *   Select a Voice Model.
    *   (Optional) Tweak the "Personality System Prompt".
    *   Click **GENERATE VIDEO**.

4.  **Watch & Download:**
    Follow the real-time status logs. Once complete, the video player will appear, and a download link will be generated.

## 🎥 Demo

Check out the included demo video to see NarrateIt in action!

<video src="Demo/MangaTest_narrated.mp4" controls width="100%"></video>

> *Note: If the video above doesn't play in your markdown viewer, you can [view it directly here](Demo/MangaTest_narrated.mp4).*

## ✨ Features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
