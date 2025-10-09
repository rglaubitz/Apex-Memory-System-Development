#!/usr/bin/env python3
"""
Export Fine-Tuned Model for Semantic-Router Integration

This script exports the fine-tuned model in HuggingFace format for use
with semantic-router's HuggingFaceEncoder.

Usage:
    python export_model.py \
        --input ../models/apex-logistics-embeddings-v1 \
        --output ../models/apex-logistics-embeddings-v1-export
"""

import argparse
import logging
from pathlib import Path
import shutil

from sentence_transformers import SentenceTransformer

# Reason: Configure logging for export progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_model(input_path: str, output_path: str = None):
    """
    Export fine-tuned model in HuggingFace transformer format.

    The model is already saved in HuggingFace format by sentence-transformers,
    so this script primarily validates and optionally copies to a new location.

    Args:
        input_path: Path to fine-tuned model directory
        output_path: Optional output path (if different from input)
    """
    logger.info(f"Loading model from: {input_path}")

    # Load the fine-tuned model
    model = SentenceTransformer(input_path)

    # Validate model structure
    input_dir = Path(input_path)
    required_files = ['config.json', 'pytorch_model.bin']

    logger.info("Validating model files...")
    for required_file in required_files:
        file_path = input_dir / required_file
        if not file_path.exists():
            # Try in subdirectory (sentence-transformers may save in '0_Transformer/')
            alt_path = input_dir / '0_Transformer' / required_file
            if alt_path.exists():
                logger.info(f"  ✅ Found {required_file} in 0_Transformer/")
            else:
                logger.warning(f"  ⚠️ Missing {required_file}")
        else:
            logger.info(f"  ✅ {required_file}")

    # Test embedding generation
    logger.info("Testing embedding generation...")
    test_query = "show all trucks owned by OpenHaul"
    embedding = model.encode(test_query)
    logger.info(f"  ✅ Generated embedding: dimension={len(embedding)}")

    # Copy to output path if specified
    if output_path and output_path != input_path:
        logger.info(f"Copying model to: {output_path}")
        output_dir = Path(output_path)
        if output_dir.exists():
            logger.warning(f"Output directory exists, removing: {output_path}")
            shutil.rmtree(output_dir)
        shutil.copytree(input_dir, output_dir)
        logger.info(f"  ✅ Model copied successfully")
    else:
        output_path = input_path

    # Print integration instructions
    logger.info("\n" + "="*80)
    logger.info("✅ Model export complete!")
    logger.info("="*80)
    logger.info("\nIntegration instructions:")
    logger.info("\n1. Update semantic_classifier.py:")
    logger.info("   Replace OpenAIEncoder with HuggingFaceEncoder:\n")
    logger.info("   from semantic_router.encoders import HuggingFaceEncoder")
    logger.info(f"   self.encoder = HuggingFaceEncoder(name='{output_path}')\n")
    logger.info("2. Run stratified test:")
    logger.info("   cd /Users/richardglaubitz/Projects/apex-memory-system")
    logger.info("   curl -s -X DELETE http://localhost:8000/api/v1/query/cache")
    logger.info("   python3 scripts/difficulty_stratified_test.py")
    logger.info("\n3. Compare results vs OpenAI baseline:")
    logger.info("   - Target: Medium ≥85% (currently 67.8%)")
    logger.info("   - Target: Hard ≥75% (currently 60.0%)")
    logger.info("   - Target: Graph ≥80% (currently 66.0%)")
    logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Export fine-tuned model for semantic-router integration'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to fine-tuned model directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Optional output path (defaults to input path)'
    )

    args = parser.parse_args()

    export_model(args.input, args.output)


if __name__ == '__main__':
    main()
