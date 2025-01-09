import os
import shutil

import argparse
import json

from src.downloader import GitHubRepoDownloader
from src.threat_model import AIThreatModel
from src.diagram_generator import DiagramGenerator

from src.vuln_engine.xss import XSSVulnerabilityScanner

OUTPUT_DIR = "outputs/"
def main():
    parser = argparse.ArgumentParser(description="Run AI threat model on a GitHub repository.")
    
    parser.add_argument(
        "--repo_url",
        type=str,
        default=os.getenv("REPO_URL"),
        help="URL of the GitHub repository to analyze. Defaults to the REPO_URL environment variable."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key. Defaults to the OPENAI_API_KEY environment variable."
    )
    parser.add_argument(
        "--download_path",
        type=str,
        default="./cloned_repo",
        help="Path to download the GitHub repository."
    )
    args = parser.parse_args()

    if not args.repo_url:
        print("Error: GitHub repository URL (--repo_url) or REPO_URL environment variable must be set.")
        return
    if not args.api_key:
        print("Error: OpenAI API key (--api_key) or OPENAI_API_KEY environment variable must be set.")
        return

    print("Downloading repository...")
    downloader = GitHubRepoDownloader(args.repo_url, args.download_path)
    downloader.download_repo()

    # Generate the architecture diagram
    #print("Generating architecture diagram...")
    #diagram_generator = DiagramGenerator(args.download_path)
    #diagram_generator.run()

    print("Analyzing repository...")
    ai_threat_model = AIThreatModel(args.download_path, args.api_key)
    report = ai_threat_model.analyze_repo()

    with open(OUTPUT_DIR+"analysis_report.json", "w") as f:
        json.dump(report, f, indent=4)
        print("Report saved to analysis_report.json\n\n")

    analysis = ai_threat_model.perform_analysis()
    print(f"\n{analysis}")

    print(f"\n\nCleaning up downloaded repository at {args.download_path}...")
    shutil.rmtree(args.download_path)

if __name__ == "__main__":
    main()
