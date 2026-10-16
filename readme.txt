AWS Cost Heatmap

Run locally:
1. Install Python dependencies: pip install -r requirements.txt
2. Start the app: streamlit run app.py
3. Open the local URL shown in the terminal.

The app requests AWS credentials to query Cost Explorer.

Docker:
1. Build: docker build -t aws-cost-heatmap .
2. Run: docker run -p 8501:8501 aws-cost-heatmap

