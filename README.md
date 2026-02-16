# GitHub Profile Analytics API

[![Tests](https://img.shields.io/badge/tests-40%20passed-brightgreen)](https://github.com)
[![Coverage](https://img.shields.io/badge/coverage-81%25-green)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688)](https://fastapi.tiangolo.com)

> **Dynamic SVG badges for GitHub profiles** - Showcase your GitHub stats, streaks, languages, trophies, contribution heatmap, and animated snake!

## 🚀 Live Demo

```markdown
![Stats](https://your-api.onrender.com/stats?user=MUKUL-PRASAD-SIGH)
![Streak](https://your-api.onrender.com/streak?user=MUKUL-PRASAD-SIGH)
![Languages](https://your-api.onrender.com/languages?user=MUKUL-PRASAD-SIGH)
![Trophy](https://your-api.onrender.com/trophy?user=MUKUL-PRASAD-SIGH)
![Heatmap](https://your-api.onrender.com/heatmap?user=MUKUL-PRASAD-SIGH)
![Snake](https://your-api.onrender.com/snake?user=MUKUL-PRASAD-SIGH)
```

## ✨ Features

### 📊 `/stats` - GitHub Statistics Card
- Total stars, commits, PRs, issues
- Follower count and repository count
- Animated SVG with smooth transitions
- Dark/light theme support

### 🔥 `/streak` - Contribution Streak
- Current streak with fire emoji 🔥
- Longest streak tracking
- Total contributions count
- Date range display

### 💻 `/languages` - Top Programming Languages
- Horizontal bar chart
- Official GitHub language colors
- Percentage calculations
- Customizable limit (default: 5)

### 🏆 `/trophy` - Achievement Badges
- Tiered system: SSS, SS, S, A, B
- Based on commits, stars, followers, PRs, issues
- Color-coded by achievement level
- Emoji indicators

### 📅 `/heatmap` - Contribution Calendar
- GitHub-style contribution grid
- 53 weeks of data
- Color-coded by activity level
- Animated cells

### 🐍 `/snake` - Animated Contribution Snake
- Snake eats contributions
- Dynamic path generation
- Infinite loop animation
- Based on actual contribution data

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115.0
- **Language**: Python 3.10+
- **API**: GitHub GraphQL API
- **Caching**: In-memory (Redis-ready)
- **Testing**: Pytest with 81% coverage
- **Deployment**: Render / Railway / Vercel

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/MUKUL-PRASAD-SIGH/github-stats-api.git
cd github-stats-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your GitHub token
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | ✅ Yes |
| `CACHE_TTL` | Cache expiration time (seconds) | ❌ No (default: 3600) |
| `API_HOST` | Server host | ❌ No (default: 0.0.0.0) |
| `API_PORT` | Server port | ❌ No (default: 8080) |

### Getting a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `read:user`, `repo`
4. Copy the token and add to `.env`

## 📖 API Documentation

### Base URL
```
https://your-api.onrender.com
```

### Endpoints

#### `/stats`
```
GET /stats?user={username}&theme={dark|light}
```
**Parameters:**
- `user` (required): GitHub username
- `theme` (optional): `dark` or `light` (default: `dark`)

#### `/streak`
```
GET /streak?user={username}&theme={dark|light}
```

#### `/languages`
```
GET /languages?user={username}&limit={number}&theme={dark|light}
```
**Parameters:**
- `limit` (optional): Number of languages to show (default: 5)

#### `/trophy`
```
GET /trophy?user={username}&theme={dark|light}
```

#### `/heatmap`
```
GET /heatmap?user={username}&theme={dark|light}
```

#### `/snake`
```
GET /snake?user={username}&theme={dark|light}
```

## 🚀 Deployment

### Deploy to Render (Recommended)

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `github-stats-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variable:
   - `GITHUB_TOKEN`: Your GitHub token
7. Click "Create Web Service"

### Deploy to Railway

1. Click: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)
2. Connect your GitHub repository
3. Add `GITHUB_TOKEN` environment variable
4. Deploy!

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Test Results:**
- ✅ 40 tests passed
- 📊 81% code coverage
- 🎯 All endpoints tested
- 🔄 Caching tested
- ⚠️ Error handling tested

## 📁 Project Structure

```
github-stats-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── cache.py             # Caching layer
│   ├── github.py            # GitHub API client
│   ├── endpoints/           # API endpoints
│   │   ├── stats.py
│   │   ├── streak.py
│   │   ├── languages.py
│   │   ├── trophy.py
│   │   ├── heatmap.py
│   │   └── snake.py
│   └── utils/               # Utility functions
│       ├── calculations.py
│       ├── streak.py
│       ├── languages.py
│       ├── trophy.py
│       ├── heatmap.py
│       ├── snake.py
│       └── svg_helpers.py
├── tests/                   # Test suite
│   ├── test_endpoints.py
│   ├── test_utils.py
│   └── test_cache.py
├── requirements.txt
├── .env.example
├── pytest.ini
└── README.md
```

## 🎨 Customization

### Themes
Both `dark` and `light` themes are supported for all endpoints.

### Colors
Language colors follow GitHub's official color scheme.

### Cache
Default cache TTL is 1 hour. Modify `CACHE_TTL` environment variable to change.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [GitHub GraphQL API](https://docs.github.com/en/graphql)

## 📧 Contact

**Mukul Prasad** - [@MUKUL-PRASAD-SIGH](https://github.com/MUKUL-PRASAD-SIGH)

Project Link: [https://github.com/MUKUL-PRASAD-SIGH/github-stats-api](https://github.com/MUKUL-PRASAD-SIGH/github-stats-api)

---

⭐ **Star this repo if you find it useful!**
