"""Model registry for Mimir AI - Manage multiple LLM models"""
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ModelCategory(Enum):
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"
    CODING = "coding"
    EMBEDDING = "embedding"

@dataclass
class ModelInfo:
    """Information about an AI model"""
    name: str
    display_name: str
    category: ModelCategory
    size_gb: float
    description: str
    use_cases: List[str]
    requires_gpu: bool = False
    recommended_ram_gb: int = 4

class ModelRegistry:
    """Registry of available AI models for Mimir"""
    
    MODELS = {
        # Fast models (1-2GB RAM)
        "tinyllama": ModelInfo(
            name="tinyllama",
            display_name="TinyLlama",
            category=ModelCategory.FAST,
            size_gb=0.5,
            description="Ultra-fast model for basic tasks. Best for low-RAM systems.",
            use_cases=["Basic Q&A", "Simple commands", "Quick responses"],
            recommended_ram_gb=1
        ),
        "phi": ModelInfo(
            name="phi",
            display_name="Phi-2",
            category=ModelCategory.FAST,
            size_gb=1.5,
            description="Microsoft's small but capable model. Good balance of speed and quality.",
            use_cases=["General Q&A", "Command suggestions", "Documentation"],
            recommended_ram_gb=2
        ),
        "gemma": ModelInfo(
            name="gemma",
            display_name="Gemma 2B",
            category=ModelCategory.FAST,
            size_gb=1.6,
            description="Google's lightweight model. Fast and accurate.",
            use_cases=["General assistance", "Command generation", "Explanations"],
            recommended_ram_gb=2
        ),
        
        # Balanced models (2-4GB RAM)
        "mistral": ModelInfo(
            name="mistral",
            display_name="Mistral 7B",
            category=ModelCategory.BALANCED,
            size_gb=4.1,
            description="Excellent all-rounder. Great for most tasks.",
            use_cases=["Complex Q&A", "Script generation", "System analysis"],
            recommended_ram_gb=4
        ),
        "llama2": ModelInfo(
            name="llama2",
            display_name="Llama 2 7B",
            category=ModelCategory.BALANCED,
            size_gb=3.8,
            description="Meta's popular model. Reliable and well-tested.",
            use_cases=["General purpose", "Help desk", "Learning assistant"],
            recommended_ram_gb=4
        ),
        "orca-mini": ModelInfo(
            name="orca-mini",
            display_name="Orca Mini",
            category=ModelCategory.BALANCED,
            size_gb=3.5,
            description="Microsoft Orca-2 distilled model. Good reasoning.",
            use_cases=["Reasoning tasks", "Problem solving", "Code assistance"],
            recommended_ram_gb=4
        ),
        
        # Powerful models (8GB+ RAM)
        "mixtral": ModelInfo(
            name="mixtral",
            display_name="Mixtral 8x7B",
            category=ModelCategory.POWERFUL,
            size_gb=8.5,
            description="High-performance MoE model. Best quality.",
            use_cases=["Complex reasoning", "Advanced scripting", "Deep analysis"],
            requires_gpu=True,
            recommended_ram_gb=8
        ),
        "llama3": ModelInfo(
            name="llama3",
            display_name="Llama 3 8B",
            category=ModelCategory.POWERFUL,
            size_gb=4.7,
            description="Meta's latest model. State-of-the-art performance.",
            use_cases=["Cutting-edge tasks", "Complex reasoning", "Expert assistance"],
            recommended_ram_gb=6
        ),
        
        # Coding models
        "codellama": ModelInfo(
            name="codellama",
            display_name="CodeLlama 7B",
            category=ModelCategory.CODING,
            size_gb=3.8,
            description="Specialized for code generation and programming tasks.",
            use_cases=["Code generation", "Script writing", "Debugging assistance"],
            recommended_ram_gb=4
        ),
        "deepseek-coder": ModelInfo(
            name="deepseek-coder",
            display_name="DeepSeek Coder",
            category=ModelCategory.CODING,
            size_gb=4.8,
            description="Advanced coding model. Excellent for programming.",
            use_cases=["Complex code generation", "Multi-language support", "Code review"],
            recommended_ram_gb=6
        ),
    }
    
    @classmethod
    def get_all_models(cls) -> Dict[str, ModelInfo]:
        """Get all available models"""
        return cls.MODELS
    
    @classmethod
    def get_model(cls, name: str) -> Optional[ModelInfo]:
        """Get model info by name"""
        return cls.MODELS.get(name)
    
    @classmethod
    def get_models_by_category(cls, category: ModelCategory) -> List[ModelInfo]:
        """Get models filtered by category"""
        return [m for m in cls.MODELS.values() if m.category == category]
    
    @classmethod
    def get_installed_models(cls) -> List[str]:
        """Get models actually installed in Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
        except:
            pass
        return []
    
    @classmethod
    def recommend_model(cls, ram_gb: float) -> str:
        """Recommend a model based on available RAM"""
        if ram_gb >= 16:
            return "mixtral"
        elif ram_gb >= 8:
            return "llama3"
        elif ram_gb >= 6:
            return "mistral"
        elif ram_gb >= 4:
            return "phi"
        else:
            return "tinyllama"
