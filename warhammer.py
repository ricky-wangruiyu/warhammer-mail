name: Warhammer Daily
on:
  push:
  workflow_dispatch:
  schedule:
    - cron: "16 1 * * *"

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install requests beautifulsoup4
      - name: Run script
        run: python warhammer.py
        env:
          SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
          EMAIL_AUTH_CODE: ${{ secrets.EMAIL_AUTH_CODE }}
          RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
