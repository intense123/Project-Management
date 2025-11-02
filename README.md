# Apex AI Chatbot

A modern, full-stack AI chatbot application with clean professional UI and dark mode. Built with React, Flask, and powered by Anthropic's Claude API.

## ✨ Features

- **💾 Conversation Persistence**: All chats automatically saved to browser
- **📝 Multiple Conversations**: Create and manage multiple chat threads
- **🔄 Switch Between Chats**: Click any conversation in the sidebar to switch
- **🎨 Clean Modern Design**: Professional UI with dark mode support
- **✨ Glowing Effects**: Beautiful green glowing accents in dark mode
- **⚡ Fast Responses**: Optimized with Claude 3 Haiku for speed (~2 seconds)
- **💬 Real-time Chat**: Seamless conversation with context awareness
- **🌙 Dark/Light Mode**: Toggle between modes with glowing effects
- **📱 Responsive**: Works on desktop, tablet, and mobile
- **🗂️ Sidebar**: Collapsible sidebar to view all conversations

## 🛠️ Tech Stack

**Frontend:** React 18, Vite, Axios  
**Backend:** Flask, Anthropic AI (Claude 3 Haiku)  
**Styling:** Modern CSS with dark mode and glowing effects

## 📋 Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- pip
- Anthropic API key

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
# Replace 'your_api_key_here' with your actual Anthropic API key

python app.py
```
Backend runs on `http://localhost:5001`

**⚠️ Important:** You must create a `.env` file in the `backend/` directory with your Anthropic API key before running the server.

### 2. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

### 3. Access the App
Open your browser: **http://localhost:3000**

## 🎮 How to Use

1. **Start Chatting**: Type your message or click a suggestion card
2. **New Chat**: Click "+ New Chat" button to start a new conversation
3. **Switch Chats**: Click any conversation in the sidebar to switch to it
4. **Delete Chat**: Hover over a conversation and click the × button
5. **Toggle Sidebar**: Click ◀/☰ button to show/hide the sidebar
6. **Dark Mode**: Click the 🌙/☀️ button to toggle dark mode with glowing effects
7. **Auto-Save**: All conversations are automatically saved in your browser

## 📁 Project Structure

```
project-1/
├── backend/          # Flask API
│   ├── app.py       # Main server (port 5001)
│   └── requirements.txt
│
└── frontend/         # React + Vite
    ├── src/
    │   ├── components/
    │   ├── App.jsx
    │   └── App.css  # Dark mode & glowing effects
    └── package.json
```

## 🔌 API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat` - Send message, get AI response
- `POST /api/chat/stream` - Streaming responses (future)

## 🎨 Design Highlights

- **Dark Mode**: Toggle with 🌙/☀️ button
- **Glowing Effects**: Green accents that glow in dark mode
- **Smooth Animations**: Message slide-ins and hover effects
- **Clean Layout**: Professional, minimal design
- **Responsive**: Works on all screen sizes

## ⚙️ Configuration

**AI Model:** Claude 3 Haiku (fast responses)  
**API Key:** Set in `backend/.env` file as `ANTHROPIC_API_KEY`  
**Colors:** Customize in `frontend/src/App.css`  
**Max Tokens:** 2048 (configurable in `backend/app.py`)

### Setting up .env file:
Create a file named `.env` in the `backend/` directory:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```
**Never commit the .env file to git** - it's already in `.gitignore`

## 🐛 Troubleshooting

**Backend won't start:**
- Activate venv: `source venv/bin/activate`
- Check port 5001: `lsof -i :5001`
- **Verify `.env` file exists** with `ANTHROPIC_API_KEY` set
- Error "ANTHROPIC_API_KEY not found"? Create the `.env` file in `backend/` directory

**Frontend issues:**
- Clear cache: `rm -rf node_modules && npm install`
- Check port 3000: `lsof -i :3000`

**Slow responses:**
- Already optimized with Claude 3 Haiku (~2 seconds)

## 📌 Key Features Summary

✅ Save & manage multiple conversations  
✅ Auto-save to browser (localStorage)  
✅ Switch between chats easily  
✅ Clean modern UI with dark mode  
✅ Beautiful glowing effects  
✅ Fast AI responses (~2 seconds)  
✅ Context-aware conversations  
✅ Collapsible sidebar  
✅ "Apex" branding throughout  

## 🎓 About

Created for Project Management Course - 8th Semester  
Educational project demonstrating full-stack development with modern UI/UX.

---

**Enjoy chatting with Apex AI!** 🚀✨

