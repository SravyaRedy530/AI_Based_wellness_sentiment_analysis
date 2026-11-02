import logging
import re
from typing import Dict, Any, List
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline
from keybert import KeyBERT

logger = logging.getLogger(__name__)

# Ensure VADER lexicon is present
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)


class AIService:
    """
    Core AI Engine for MoodMentor.
    Integrates HuggingFace DistilBERT for emotion classification,
    NLTK VADER for granular sentiment polarity,
    KeyBERT for contextual keyphrase extraction,
    and an evidence-based clinical wellness suggestion generator.
    """

    _instance = None
    _emotion_classifier = None
    _vader_analyzer = None
    _keybert_model = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self):
        """Initializes AI models once at startup (Singleton pattern)."""
        logger.info("Initializing MoodMentor AI Service models...")

        # 1. Initialize VADER Analyzer
        try:
            self._vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER Sentiment Analyzer initialized successfully.")
        except Exception as e:
            logger.error("Failed to load VADER analyzer: %s", e)
            self._vader_analyzer = None

        # 2. Initialize DistilBERT Emotion Classifier
        try:
            import os
            local_model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "ekman_distilbert"))
            env_model = os.getenv("HF_EMOTION_MODEL", "bhadresh-savani/distilbert-base-uncased-emotion")
            use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() in ("true", "1", "yes")

            if (use_local or env_model in ("models/ekman_distilbert", local_model_dir)) and os.path.exists(local_model_dir):
                model_name = local_model_dir
                logger.info("Loading fine-tuned local Ekman model from: %s", local_model_dir)
            else:
                model_name = env_model
                logger.info("Using HuggingFace emotion model: %s", model_name)

            self._emotion_classifier = pipeline(
                "text-classification",
                model=model_name,
                top_k=None,
                truncation=True,
                max_length=512
            )
            logger.info("DistilBERT Emotion Classifier initialized successfully.")
        except Exception as e:
            logger.error("Failed to load HuggingFace emotion model: %s", e)
            self._emotion_classifier = None

        # 3. Initialize KeyBERT
        try:
            self._keybert_model = KeyBERT()
            logger.info("KeyBERT model initialized successfully.")
        except Exception as e:
            logger.error("Failed to load KeyBERT: %s", e)
            self._keybert_model = None

    def analyze_emotion_distilbert(self, text: str) -> Dict[str, Any]:
        """
        Classifies emotional states using DistilBERT.
        Labels: joy, sadness, anger, fear, love, surprise
        """
        if not text or not text.strip():
            return {
                "primary_emotion": "neutral",
                "confidence": 0.0,
                "all_emotions": []
            }

        cleaned_text = text.strip()[:1000]

        if self._emotion_classifier:
            try:
                results = self._emotion_classifier(cleaned_text)
                # results is a list of lists of dicts e.g. [[{'label': 'joy', 'score': 0.98}, ...]]
                scores = results[0] if isinstance(results, list) and len(results) > 0 else []
                # Sort descending by score
                scores = sorted(scores, key=lambda x: x["score"], reverse=True)
                primary = scores[0] if scores else {"label": "neutral", "score": 0.5}

                return {
                    "primary_emotion": primary["label"],
                    "confidence": round(float(primary["score"]), 4),
                    "all_emotions": [
                        {"emotion": item["label"], "score": round(float(item["score"]), 4)}
                        for item in scores
                    ]
                }
            except Exception as e:
                logger.error("DistilBERT inference error: %s", e)

        # Fallback heuristic if transformer fails
        return self._heuristic_emotion_fallback(cleaned_text)

    def analyze_sentiment_vader(self, text: str) -> Dict[str, Any]:
        """
        Computes sentiment polarity scores using NLTK VADER.
        """
        if not text or not text.strip():
            return {
                "compound": 0.0,
                "positive": 0.0,
                "neutral": 1.0,
                "negative": 0.0,
                "label": "Neutral"
            }

        if self._vader_analyzer:
            scores = self._vader_analyzer.polarity_scores(text)
            compound = scores["compound"]
            if compound >= 0.05:
                label = "Positive"
            elif compound <= -0.05:
                label = "Negative"
            else:
                label = "Neutral"

            return {
                "compound": round(float(scores["compound"]), 4),
                "positive": round(float(scores["pos"]), 4),
                "neutral": round(float(scores["neu"]), 4),
                "negative": round(float(scores["neg"]), 4),
                "label": label
            }

        return {
            "compound": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0,
            "label": "Neutral"
        }

    def extract_keywords(self, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extracts salient keywords and keyphrases using KeyBERT.
        Falls back to statistical n-gram extraction if needed.
        """
        if not text or len(text.strip().split()) < 3:
            words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)]
            return [{"keyword": w, "relevance": 0.5} for w in list(dict.fromkeys(words))[:top_n]]

        if self._keybert_model:
            try:
                raw_keywords = self._keybert_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 2),
                    stop_words="english",
                    top_n=top_n
                )
                return [
                    {"keyword": kw, "relevance": round(float(score), 4)}
                    for kw, score in raw_keywords
                ]
            except Exception as e:
                logger.error("KeyBERT extraction error: %s", e)

        # Lightweight statistical fallback
        tokens = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        stopwords = {"this", "that", "with", "have", "from", "they", "will", "would", "there", "their", "what", "about"}
        filtered = [t for t in tokens if t not in stopwords]
        freq = {}
        for t in filtered:
            freq[t] = freq.get(t, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{"keyword": k, "relevance": round(v / max(1, len(filtered)), 4)} for k, v in sorted_tokens]

    def generate_wellness_suggestion(self, primary_emotion: str, sentiment: Dict[str, Any], keywords: List[Dict[str, Any]]) -> str:
        """
        Generates evidence-based psychological coping suggestions,
        cognitive reframing prompts, and actionable wellness exercises.
        """
        emotion = primary_emotion.lower()
        compound = sentiment.get("compound", 0.0)
        kw_list = [k["keyword"] for k in keywords[:3]]
        focus_phrase = f" relating to {', '.join(kw_list)}" if kw_list else ""

        recommendations = {
            "anger": (
                f"🔥 **Cool Down & Refocus**{focus_phrase}:\n"
                "- **Box Breathing**: Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4. Repeat 4 times to regulate cortisol.\n"
                "- **Cognitive Shift**: Ask yourself: 'What boundary was crossed, and what is one constructive step I can control right now?'\n"
                "- **Physical Discharge**: Step away from screens for a 10-minute brisk walk or dynamic stretching."
            ),
            "fear": (
                f"🛡️ **Grounding & Anxiety Relief**{focus_phrase}:\n"
                "- **5-4-3-2-1 Sensory Grounding**: Name 5 things you can see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.\n"
                "- **Worst-Best-Likely Reframe**: What's the worst that could happen? What's the best? What is the most realistic outcome?\n"
                "- **Action Chunking**: Break down what feels overwhelming into a single 5-minute task you can execute today."
            ),
            "sadness": (
                f"🌱 **Gentle Self-Compassion & Uplift**{focus_phrase}:\n"
                "- **Acknowledge Without Judgment**: Give yourself permission to feel down without self-criticism. Feelings are temporary visitors.\n"
                "- **Behavioral Activation**: Do one tiny nurturing activity: brew a warm cup of herbal tea, listen to an acoustic playlist, or step into natural sunlight.\n"
                "- **Connection**: Consider reaching out to a trusted colleague, friend, or writing a brief gratitude note."
            ),
            "joy": (
                f"✨ **Savoring & Emotional Anchoring**{focus_phrase}:\n"
                "- **Savor the Moment**: Take 60 seconds to vividly absorb this positive experience so your neural pathways encode it deeply.\n"
                "- **Gratitude Amplification**: Write down what specific action, person, or effort made this joyful moment possible.\n"
                "- **Pay It Forward**: Share your positive energy with a teammate or loved one through a genuine compliment."
            ),
            "love": (
                f"💖 **Fostering Connection & Warmth**{focus_phrase}:\n"
                "- **Affirmation**: Cherish and celebrate this relational warmth and mutual support.\n"
                "- **Reciprocity**: Send a brief message expressing your appreciation to those who bring peace to your life.\n"
                "- **Self-Love**: Extend the same kindness and understanding to yourself as you do to others."
            ),
            "surprise": (
                f"💡 **Adaptability & Curiosity**{focus_phrase}:\n"
                "- **Curiosity Mindset**: Treat unexpected developments as information rather than disruptions.\n"
                "- **Pause Before Reacting**: Take two deep diaphragmatic breaths to transition from surprise to deliberate strategy.\n"
                "- **Reflect**: How does this new perspective offer an unanticipated learning opportunity?"
            ),
            "disgust": (
                f"🛡️ **Boundary Setting & Environmental Reset**{focus_phrase}:\n"
                "- **Identify the Boundary**: Disgust often signals an ethical, sensory, or interpersonal boundary violation. Identify specifically what felt unacceptable.\n"
                "- **Sensory Detox**: Step away from the triggering environment into fresh air, drink cool water, or wash your hands/face mindfully.\n"
                "- **Constructive Distancing**: Focus on establishing clear, polite boundaries while disengaging from toxic dialogue or gossip."
            )
        }

        default_suggestion = (
            f"🌿 **Mindful Presence**{focus_phrase}:\n"
            "- Take three slow, purposeful breaths to ground yourself in the present moment.\n"
            "- Note your energy level and allow yourself an intentional micro-break away from digital demands.\n"
            "- Set one clear, manageable intention for the remainder of your day."
        )

        return recommendations.get(emotion, default_suggestion)

    def suggest_activities(self, primary_emotion: str, sentiment: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generates tailored wellness and coping activities based on emotional state.
        Supported emotions: Joy, Fear, Sadness, Anger, Love, Surprise, Neutral.
        """
        emo = primary_emotion.lower()
        compound = sentiment.get("compound", 0.0)

        activities_catalog = {
            "joy": [
                {
                    "icon": "🌟",
                    "title": "Gratitude Anchoring",
                    "description": "Write down 3 specific details that made this moment special to deeply encode the positive memory in your neural pathways.",
                    "duration": "5 mins"
                },
                {
                    "icon": "🤝",
                    "title": "Pay It Forward",
                    "description": "Share your positive energy with a colleague, friend, or loved one through a genuine compliment or uplifting message.",
                    "duration": "2 mins"
                },
                {
                    "icon": "🏃",
                    "title": "Celebratory Movement",
                    "description": "Take a brisk walk in natural sunlight or dance to an upbeat track to turn your joyful energy into vitality.",
                    "duration": "15 mins"
                }
            ],
            "fear": [
                {
                    "icon": "🫁",
                    "title": "4-7-8 Breathing Exercise",
                    "description": "Inhale quietly through your nose for 4s, hold for 7s, and exhale completely with a whoosh sound for 8s. Repeat 4 times to calm your nervous system.",
                    "duration": "3 mins"
                },
                {
                    "icon": "🛡️",
                    "title": "5-4-3-2-1 Sensory Grounding",
                    "description": "Acknowledge 5 things you see, 4 things you can touch, 3 sounds you hear, 2 scents you smell, and 1 taste.",
                    "duration": "4 mins"
                },
                {
                    "icon": "📝",
                    "title": "Action Chunking & Worry Dump",
                    "description": "Write down what feels overwhelming and isolate a single 5-minute micro-action you can take control of right now.",
                    "duration": "5 mins"
                }
            ],
            "sadness": [
                {
                    "icon": "🍵",
                    "title": "Gentle Soothing Ritual",
                    "description": "Brew a warm cup of herbal chamomile or green tea, dim bright harsh lights, and allow your body to relax without screens.",
                    "duration": "10 mins"
                },
                {
                    "icon": "🌱",
                    "title": "Natural Sunlight Exposure",
                    "description": "Step outdoors or sit near a sunny window for 10-15 minutes of direct sunlight to support natural dopamine and serotonin production.",
                    "duration": "15 mins"
                },
                {
                    "icon": "🎵",
                    "title": "Comfort Acoustic Listening",
                    "description": "Listen to comforting acoustic or instrumental music that acknowledges your feelings without dragging you into negative rumination.",
                    "duration": "15 mins"
                }
            ],
            "anger": [
                {
                    "icon": "🧊",
                    "title": "Box Breathing & Cold Splash",
                    "description": "Inhale 4s, hold 4s, exhale 4s, hold 4s. Splash cold water on your wrists and face to activate the mammalian dive reflex.",
                    "duration": "3 mins"
                },
                {
                    "icon": "🚶",
                    "title": "Physical Step-Away",
                    "description": "Remove yourself from the immediate environment for 10 minutes. Avoid replying to messages or emails until heart rate normalizes.",
                    "duration": "10 mins"
                },
                {
                    "icon": "✍️",
                    "title": "Unfiltered Release Writing",
                    "description": "Write raw unfiltered feelings on a physical paper, re-read once to identify your underlying boundary, then discard or shred it.",
                    "duration": "5 mins"
                }
            ],
            "love": [
                {
                    "icon": "💌",
                    "title": "Heartfelt Appreciation Note",
                    "description": "Send a short note expressing genuine appreciation to someone who brings peace, warmth, or trust to your life.",
                    "duration": "3 mins"
                },
                {
                    "icon": "🧘",
                    "title": "Loving-Kindness (Metta) Pause",
                    "description": "Close your eyes and send silent wishes of safety, health, and peace to yourself, your loved ones, and your community.",
                    "duration": "5 mins"
                },
                {
                    "icon": "🌿",
                    "title": "Self-Compassion Check-in",
                    "description": "Treat yourself with the exact same tenderness and non-judgmental grace that you readily offer to those you care about.",
                    "duration": "5 mins"
                }
            ],
            "surprise": [
                {
                    "icon": "⏸️",
                    "title": "Strategic Pause & Settle",
                    "description": "Take two slow diaphragmatic breaths to transition from startled reaction into mindful observation.",
                    "duration": "2 mins"
                },
                {
                    "icon": "💡",
                    "title": "Curiosity Reframe",
                    "description": "Ask yourself: 'What unanticipated opportunity or valuable learning does this unexpected situation present?'",
                    "duration": "5 mins"
                },
                {
                    "icon": "🧭",
                    "title": "Fact vs Assumption Check",
                    "description": "Separate known factual information from immediate speculative assumptions before deciding on next steps.",
                    "duration": "5 mins"
                }
            ],
            "disgust": [
                {
                    "icon": "🛡️",
                    "title": "Healthy Boundary Audit",
                    "description": "Identify what environmental condition or communication crossed your personal boundaries, and define a clear boundary to protect your peace.",
                    "duration": "5 mins"
                },
                {
                    "icon": "🌿",
                    "title": "Sensory Cleansing Micro-Break",
                    "description": "Step away into natural air, wash hands and face with cool water, and sip cold water to reset sensory overstimulation.",
                    "duration": "5 mins"
                },
                {
                    "icon": "🧘",
                    "title": "Mindful Physical Space Cleanse",
                    "description": "Tidy up your immediate workspace or desk. Decluttering physical space sends strong psychological signals of control and clarity.",
                    "duration": "10 mins"
                }
            ],
            "neutral": [
                {
                    "icon": "🎯",
                    "title": "Single Daily Priority Focus",
                    "description": "Pick the one single high-impact task or creative endeavor you want to dedicate your baseline mental clarity to today.",
                    "duration": "5 mins"
                },
                {
                    "icon": "🧘",
                    "title": "Spine & Posture Breath Reset",
                    "description": "Stand up, gently roll your shoulders back, stretch your arms overhead, and take 5 slow, energizing deep breaths.",
                    "duration": "3 mins"
                },
                {
                    "icon": "📚",
                    "title": "Mindful Intellectual Reading",
                    "description": "Spend 15 distraction-free minutes reading a thought-provoking article, book chapter, or listening to a wellness podcast.",
                    "duration": "15 mins"
                }
            ]
        }

        return activities_catalog.get(emo, activities_catalog["neutral"])

    def generate_personalized_suggestions(self, primary_emotion: str) -> Dict[str, Any]:
        """
        Generates personalized suggestions strictly mapped to predicted emotion:
        - Joy: Celebrate achievements, Share appreciation, Take photos
        - Fear: Breathing exercise, Grounding, Positive affirmations, Mindfulness
        - Sadness: Music, Walk, Friend, Journaling
        Also supports Anger, Love, Surprise, and Neutral.
        """
        emo = primary_emotion.lower()

        suggestions_map = {
            "joy": {
                "simple": [
                    "Celebrate achievements",
                    "Share appreciation",
                    "Take photos"
                ],
                "detailed": [
                    {
                        "title": "Celebrate achievements",
                        "description": "Acknowledge your milestones and personal growth. Treat yourself to a favorite meal, activity, or quiet reward to celebrate what you have accomplished.",
                        "icon": "🎉",
                        "category": "Celebration"
                    },
                    {
                        "title": "Share appreciation",
                        "description": "Send a heartfelt message, email, or note to teammates, friends, or mentors expressing sincere appreciation for their presence and support.",
                        "icon": "💌",
                        "category": "Connection"
                    },
                    {
                        "title": "Take photos",
                        "description": "Capture a photo of this special moment, your surroundings, or yourself smiling so your future self can look back and revisit this positive memory.",
                        "icon": "📸",
                        "category": "Memory"
                    }
                ]
            },
            "fear": {
                "simple": [
                    "Breathing exercise",
                    "Grounding",
                    "Positive affirmations",
                    "Mindfulness"
                ],
                "detailed": [
                    {
                        "title": "Breathing exercise",
                        "description": "Perform 4-7-8 breathing: Inhale slowly through your nose for 4 seconds, hold your breath for 7 seconds, and exhale smoothly through your mouth for 8 seconds. Repeat 4 times.",
                        "icon": "🫁",
                        "category": "Physiology"
                    },
                    {
                        "title": "Grounding",
                        "description": "Practice the 5-4-3-2-1 grounding method: name 5 objects you see, 4 you can touch, 3 sounds you hear, 2 scents you smell, and 1 taste to bring your nervous system back to safety.",
                        "icon": "🛡️",
                        "category": "Centering"
                    },
                    {
                        "title": "Positive affirmations",
                        "description": "Repeat these affirmations out loud or mentally: 'I am safe in this present moment. I am resilient, capable, and have navigated uncertainty before.'",
                        "icon": "✨",
                        "category": "Mindset"
                    },
                    {
                        "title": "Mindfulness",
                        "description": "Observe fearful thoughts as passing clouds in the sky rather than concrete facts. Allow the physical sensations to peak and dissipate without judgment.",
                        "icon": "🧘",
                        "category": "Awareness"
                    }
                ]
            },
            "sadness": {
                "simple": [
                    "Music",
                    "Walk",
                    "Friend",
                    "Journaling"
                ],
                "detailed": [
                    {
                        "title": "Music",
                        "description": "Listen to a comforting acoustic or uplifting instrumental playlist to stimulate auditory dopamine and soothe your emotional state.",
                        "icon": "🎵",
                        "category": "Auditory"
                    },
                    {
                        "title": "Walk",
                        "description": "Step outside for a gentle 15-minute nature walk in natural daylight. Low-intensity movement encourages bilateral brain stimulation and endorphin flow.",
                        "icon": "🚶",
                        "category": "Movement"
                    },
                    {
                        "title": "Friend",
                        "description": "Reach out to a trusted friend or family member for a short phone call, text, or warm coffee chat to break feelings of isolation.",
                        "icon": "🤝",
                        "category": "Connection"
                    },
                    {
                        "title": "Journaling",
                        "description": "Write your unfiltered thoughts and feelings freely on paper to give external expression to emotional weight and promote psychological release.",
                        "icon": "✍️",
                        "category": "Expression"
                    }
                ]
            },
            "anger": {
                "simple": [
                    "Box breathing",
                    "Physical cool-down",
                    "Boundary reflection"
                ],
                "detailed": [
                    {
                        "title": "Box breathing",
                        "description": "Inhale 4s, hold 4s, exhale 4s, hold 4s. Cool down high physiological arousal before taking any action.",
                        "icon": "🧊",
                        "category": "Regulation"
                    },
                    {
                        "title": "Physical cool-down",
                        "description": "Step away from the situation for 10 minutes and take a brisk walk or splash cold water on your face.",
                        "icon": "🚶",
                        "category": "Distance"
                    },
                    {
                        "title": "Boundary reflection",
                        "description": "Identify what specific expectation or boundary was breached and formulate one calm, constructive request.",
                        "icon": "🧭",
                        "category": "Clarity"
                    }
                ]
            },
            "love": {
                "simple": [
                    "Express affection",
                    "Quality time",
                    "Self-compassion"
                ],
                "detailed": [
                    {
                        "title": "Express affection",
                        "description": "Share your appreciation with someone who brings peace, warmth, and joy to your life.",
                        "icon": "💖",
                        "category": "Connection"
                    },
                    {
                        "title": "Quality time",
                        "description": "Dedicate focused, undivided attention to a shared meal, walk, or conversation with loved ones.",
                        "icon": "☕",
                        "category": "Presence"
                    },
                    {
                        "title": "Self-compassion",
                        "description": "Extend unconditional warmth and kindness inward to yourself as readily as you do to others.",
                        "icon": "🌿",
                        "category": "Self-Care"
                    }
                ]
            },
            "surprise": {
                "simple": [
                    "Take a strategic pause",
                    "Curiosity reframing",
                    "Fact check"
                ],
                "detailed": [
                    {
                        "title": "Take a strategic pause",
                        "description": "Allow your initial adrenaline to settle with two deep diaphragmatic breaths before reacting.",
                        "icon": "⏸️",
                        "category": "Pacing"
                    },
                    {
                        "title": "Curiosity reframing",
                        "description": "Approach this unexpected twist with curiosity: 'What new perspective or advantage might this reveal?'",
                        "icon": "💡",
                        "category": "Inquiry"
                    },
                    {
                        "title": "Fact check",
                        "description": "Distinguish verified facts from immediate speculative assumptions before making your next move.",
                        "icon": "📋",
                        "category": "Assessment"
                    }
                ]
            },
            "disgust": {
                "simple": [
                    "Boundary audit",
                    "Sensory reset",
                    "Workspace cleanse"
                ],
                "detailed": [
                    {
                        "title": "Boundary audit",
                        "description": "Identify which ethical, personal, or professional boundary was crossed, and plan a clear, calm boundary to protect your well-being.",
                        "icon": "🛡️",
                        "category": "Boundaries"
                    },
                    {
                        "title": "Sensory reset",
                        "description": "Step into open fresh air, wash hands and face with cool water, and take 3 deep grounding breaths to clear sensory overstimulation.",
                        "icon": "🌿",
                        "category": "Sensory"
                    },
                    {
                        "title": "Workspace cleanse",
                        "description": "Tidy up your immediate workspace or desk. Decluttering physical space sends strong psychological signals of clarity and control.",
                        "icon": "🧹",
                        "category": "Environment"
                    }
                ]
            },
            "neutral": {
                "simple": [
                    "Intention setting",
                    "Mindful reading",
                    "Spine & posture reset"
                ],
                "detailed": [
                    {
                        "title": "Intention setting",
                        "description": "Channel your baseline focus and calm into one key priority you wish to accomplish today.",
                        "icon": "🎯",
                        "category": "Focus"
                    },
                    {
                        "title": "Mindful reading",
                        "description": "Spend 15 distraction-free minutes reading an insightful article, book chapter, or educational piece.",
                        "icon": "📚",
                        "category": "Enrichment"
                    },
                    {
                        "title": "Spine & posture reset",
                        "description": "Stand up, stretch your back, roll your shoulders, and take five revitalizing deep breaths.",
                        "icon": "🧘",
                        "category": "Body"
                    }
                ]
            }
        }

        default_bundle = suggestions_map["neutral"]
        bundle = suggestions_map.get(emo, default_bundle)
        return bundle

    def analyze_full_entry(self, text: str) -> Dict[str, Any]:
        """
        Executes complete multimodal AI analysis pipeline on the provided text.
        """
        if not text or not text.strip():
            neutral_suggestions = self.generate_personalized_suggestions("neutral")
            return {
                "primary_emotion": "Neutral",
                "emotion": "Neutral",
                "emotion_confidence": 0.0,
                "confidence": 0.0,
                "confidence_percentage": 0.0,
                "all_emotions": [],
                "sentiment": {
                    "compound": 0.0,
                    "positive": 0.0,
                    "neutral": 1.0,
                    "negative": 0.0,
                    "label": "Neutral"
                },
                "sentiment_label": "Neutral",
                "sentiment_score": 0.0,
                "keywords": [],
                "suggestions": neutral_suggestions["simple"],
                "personalized_suggestions": neutral_suggestions["detailed"],
                "activities": self.suggest_activities("neutral", {}),
                "recommendations": "Enter your thoughts to receive personalized AI emotional analysis and activity suggestions.",
                "coping_suggestion": "Enter your thoughts to receive personalized AI emotional analysis and activity suggestions."
            }

        emotion_res = self.analyze_emotion_distilbert(text)
        sentiment_res = self.analyze_sentiment_vader(text)
        keywords_res = self.extract_keywords(text, top_n=5)

        primary_emo = emotion_res["primary_emotion"]
        # If confidence is very low (< 0.35) or sentiment is strictly neutral, label as Neutral
        if emotion_res["confidence"] < 0.35 and abs(sentiment_res["compound"]) < 0.05:
            primary_emo = "neutral"

        # Generate targeted suggestions matching user exact rules
        suggestions_bundle = self.generate_personalized_suggestions(primary_emo)
        activities = self.suggest_activities(primary_emo, sentiment_res)
        suggestion_text = self.generate_wellness_suggestion(
            primary_emotion=primary_emo,
            sentiment=sentiment_res,
            keywords=keywords_res
        )

        return {
            "primary_emotion": primary_emo.capitalize(),
            "emotion": primary_emo.capitalize(),
            "emotion_confidence": emotion_res["confidence"],
            "confidence": emotion_res["confidence"],
            "confidence_percentage": round(emotion_res["confidence"] * 100, 1),
            "all_emotions": emotion_res["all_emotions"],
            "sentiment": sentiment_res,
            "sentiment_label": sentiment_res.get("label", "Neutral"),
            "sentiment_score": sentiment_res.get("compound", 0.0),
            "keywords": keywords_res,
            "suggestions": suggestions_bundle["simple"],
            "personalized_suggestions": suggestions_bundle["detailed"],
            "activities": activities,
            "recommendations": suggestion_text,
            "coping_suggestion": suggestion_text
        }

    def _heuristic_emotion_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback emotional scoring if transformer pipeline is unavailable."""
        t = text.lower()
        scores = {
            "joy": len(re.findall(r"\b(happy|glad|excited|delighted|great|proud|blessed|cheerful|joy)\b", t)) * 0.3,
            "sadness": len(re.findall(r"\b(sad|down|depressed|unhappy|lonely|heartbroken|grief|cry)\b", t)) * 0.3,
            "anger": len(re.findall(r"\b(angry|furious|mad|annoyed|irritated|frustrated|rage)\b", t)) * 0.3,
            "fear": len(re.findall(r"\b(scared|afraid|anxious|nervous|worried|panic|terrified|stress)\b", t)) * 0.3,
            "love": len(re.findall(r"\b(love|adore|caring|cherish|affection|fond|grateful)\b", t)) * 0.3,
            "surprise": len(re.findall(r"\b(shocked|amazed|astonished|unexpected|stunned)\b", t)) * 0.3,
        }
        total = sum(scores.values())
        if total == 0:
            return {
                "primary_emotion": "neutral",
                "confidence": 0.5,
                "all_emotions": [{"emotion": "neutral", "score": 1.0}]
            }
        
        normalized = sorted(
            [{"emotion": k, "score": round(v / total, 4)} for k, v in scores.items()],
            key=lambda x: x["score"],
            reverse=True
        )
        return {
            "primary_emotion": normalized[0]["emotion"],
            "confidence": normalized[0]["score"],
            "all_emotions": normalized
        }


# Singleton instance accessor
ai_service = AIService()
