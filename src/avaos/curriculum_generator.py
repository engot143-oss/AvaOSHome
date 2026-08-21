"""
Generate the Kumon curriculum JSON file including faith topics.
"""

import json
from pathlib import Path


def create_kumon_curriculum_with_faith() -> dict:
    """Create comprehensive Kumon curriculum with integrated faith topics."""

    curriculum = {
        "version": "2.0",
        "updated": "2026-08-19",
        "subjects": {
            "math": {
                "name": "Mathematics",
                "description": "Math skills from basics to advanced",
                "color": "#FF6B6B",
                "icon": "calculator",
                "concepts": [
                    {
                        "id": "math-001",
                        "name": "Addition & Subtraction",
                        "description": "Adding and subtracting numbers",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": [],
                        "unlocks": ["math-002"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is 25 + 17?",
                            "Subtract 8 from 45"
                        ]
                    },
                    {
                        "id": "math-002",
                        "name": "Multiplication Basics",
                        "description": "Understanding multiplication",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": ["math-001"],
                        "unlocks": ["math-003"],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is 6 × 7?",
                            "12 × 3 = ?"
                        ]
                    },
                    {
                        "id": "math-003",
                        "name": "Division Basics",
                        "description": "Understanding division",
                        "level": "INTERMEDIATE",
                        "age_min": 10,
                        "prerequisites": ["math-002"],
                        "unlocks": ["math-004"],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is 20 divided by 4?",
                            "36 / 6 = ?"
                        ]
                    }
                ]
            },
            "english": {
                "name": "English",
                "description": "Reading, writing, and comprehension",
                "color": "#4ECDC4",
                "icon": "book",
                "concepts": [
                    {
                        "id": "eng-001",
                        "name": "Reading Comprehension",
                        "description": "Understanding what you read",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": [],
                        "unlocks": ["eng-002"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "Read a short story and answer questions",
                            "What was the main idea?"
                        ]
                    },
                    {
                        "id": "eng-002",
                        "name": "Vocabulary Building",
                        "description": "Learning new words",
                        "level": "INTERMEDIATE",
                        "age_min": 10,
                        "prerequisites": ["eng-001"],
                        "unlocks": [],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What does 'benevolent' mean?",
                            "Use 'persevere' in a sentence"
                        ]
                    }
                ]
            },
            "science": {
                "name": "Science",
                "description": "Biology, physics, chemistry, earth science",
                "color": "#95E1D3",
                "icon": "microscope",
                "concepts": [
                    {
                        "id": "sci-001",
                        "name": "Living Things",
                        "description": "Plants, animals, and ecosystems",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": [],
                        "unlocks": ["sci-002"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What do plants need to survive?",
                            "Name three types of animals"
                        ]
                    },
                    {
                        "id": "sci-002",
                        "name": "Water Cycle",
                        "description": "How water moves through Earth",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": ["sci-001"],
                        "unlocks": ["sci-003"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is evaporation?",
                            "Describe the water cycle"
                        ]
                    },
                    {
                        "id": "sci-003",
                        "name": "Weather Patterns",
                        "description": "Understanding weather systems",
                        "level": "INTERMEDIATE",
                        "age_min": 10,
                        "prerequisites": ["sci-002"],
                        "unlocks": [],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "How do hurricanes form?",
                            "What causes seasonal weather?"
                        ]
                    }
                ]
            },
            "faith": {
                "name": "Faith & Character",
                "description": "Spiritual development and values",
                "color": "#FFD93D",
                "icon": "heart",
                "concepts": [
                    {
                        "id": "faith-001",
                        "name": "God Loves You",
                        "description": "Understanding God's love and prayer",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": [],
                        "unlocks": ["faith-002", "faith-003"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What does it mean to pray?",
                            "How do you feel God's love?"
                        ]
                    },
                    {
                        "id": "faith-002",
                        "name": "The Bible",
                        "description": "Bible as God's Word and guide",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": ["faith-001"],
                        "unlocks": [],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "Why is the Bible important?",
                            "What Bible story stands out to you?"
                        ]
                    },
                    {
                        "id": "faith-003",
                        "name": "Kindness & Service",
                        "description": "Showing love through actions",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": ["faith-001"],
                        "unlocks": ["faith-004"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "How can you show kindness today?",
                            "Why does God want us to help others?"
                        ]
                    },
                    {
                        "id": "faith-004",
                        "name": "Integrity",
                        "description": "Doing right when no one is watching",
                        "level": "INTERMEDIATE",
                        "age_min": 12,
                        "prerequisites": ["faith-003"],
                        "unlocks": ["faith-005"],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What does integrity mean?",
                            "When is it hard to be honest?"
                        ]
                    },
                    {
                        "id": "faith-005",
                        "name": "Courage",
                        "description": "Standing for what's right",
                        "level": "INTERMEDIATE",
                        "age_min": 12,
                        "prerequisites": ["faith-004"],
                        "unlocks": ["faith-006"],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is courage?",
                            "When do you need courage?"
                        ]
                    },
                    {
                        "id": "faith-006",
                        "name": "Resisting Temptation",
                        "description": "Avoiding peer pressure and bad influences",
                        "level": "INTERMEDIATE",
                        "age_min": 12,
                        "prerequisites": ["faith-004", "faith-005"],
                        "unlocks": [],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What are warning signs of temptation?",
                            "How can you resist peer pressure?"
                        ]
                    }
                ]
            },
            "financial_literacy": {
                "name": "Financial Literacy",
                "description": "Money management and values-based decisions",
                "color": "#6BCB77",
                "icon": "dollar",
                "concepts": [
                    {
                        "id": "fin-001",
                        "name": "Money Basics",
                        "description": "Earning, saving, spending",
                        "level": "BEGINNER",
                        "age_min": 10,
                        "prerequisites": [],
                        "unlocks": ["fin-002"],
                        "mastery_threshold": 85,
                        "estimated_days": 7,
                        "sample_questions": [
                            "Where does money come from?",
                            "What is saving?"
                        ]
                    },
                    {
                        "id": "fin-002",
                        "name": "The 50/30/20 Rule",
                        "description": "Budget management: needs, wants, savings",
                        "level": "INTERMEDIATE",
                        "age_min": 12,
                        "prerequisites": ["fin-001"],
                        "unlocks": [],
                        "mastery_threshold": 80,
                        "estimated_days": 7,
                        "sample_questions": [
                            "What is the 50/30/20 rule?",
                            "How do you budget your money?"
                        ]
                    }
                ]
            }
        },
        "daily_rotation": [
            "math",
            "english",
            "science",
            "faith",
            "financial_literacy"
        ],
        "spaced_repetition_days": [1, 3, 7, 14, 30],
        "mastery_threshold_default": 80
    }

    return curriculum


def generate_curriculum_file(output_path: Path) -> None:
    """Generate and save the curriculum file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    curriculum = create_kumon_curriculum_with_faith()

    with open(output_path, 'w') as f:
        json.dump(curriculum, f, indent=2)

    print(f"Curriculum generated: {output_path}")


if __name__ == '__main__':
    from pathlib import Path
    home = Path.home()
    curriculum_dir = home / '.ava_os' / 'curriculum'
    curriculum_file = curriculum_dir / 'kumon_curriculum.json'

    generate_curriculum_file(curriculum_file)
    print("Curriculum ready for deployment!")
