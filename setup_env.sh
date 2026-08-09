#!/bin/bash
# Setup script for Urban Mobility Analytics

set -e

echo "==================================================="
echo "Urban Mobility Analytics - Setup Script"
echo "==================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Create virtual environment
echo "${YELLOW}Step 1: Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "${GREEN}✓ Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Step 2: Activate virtual environment
echo "${YELLOW}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate
echo "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 3: Install dependencies
echo "${YELLOW}Step 3: Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Create .env from template
echo "${YELLOW}Step 4: Setting up environment variables...${NC}"
if [ -f ".env" ]; then
    echo "${GREEN}✓ .env file already exists${NC}"
else
    cp .env.example .env
    echo "${GREEN}✓ Created .env from template${NC}"
    echo ""
    echo "${RED}⚠️  IMPORTANT: Edit .env and add your API keys:${NC}"
    echo "   TOMTOM_API_KEY=your_key_here"
    echo "   OPENWEATHER_API_KEY=your_key_here"
    echo ""
fi
echo ""

# Step 5: Create required directories
echo "${YELLOW}Step 5: Creating required directories...${NC}"
mkdir -p data/raw data/processed
mkdir -p logs
mkdir -p src/models/trained
mkdir -p tests
echo "${GREEN}✓ Directories created${NC}"
echo ""

# Step 6: Run tests
echo "${YELLOW}Step 6: Running validation tests...${NC}"
if python test_dashboard.py > /dev/null 2>&1; then
    echo "${GREEN}✓ All validation tests passed${NC}"
else
    echo "${RED}✗ Some tests failed (check logs)${NC}"
fi
echo ""

# Final message
echo "==================================================="
echo "${GREEN}Setup complete!${NC}"
echo "==================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start collecting data:"
echo "   python -m src.route_extraction --interval 120"
echo ""
echo "3. In another terminal, train models:"
echo "   python train_models.py"
echo ""
echo "4. Launch dashboard:"
echo "   python -m streamlit run streamlit_app/app.py"
echo ""
echo "Documentation: README_FINAL.md"
echo ""
