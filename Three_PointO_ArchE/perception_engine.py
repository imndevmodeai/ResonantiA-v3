# ResonantiA Protocol v3.1-CA - ArchE Perception Engine
# Advanced multi-modal cognitive processing framework for environmental and informational perception
# Integrates with the full ArchE ecosystem for comprehensive analysis and decision-making

import logging
import json
import time
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from datetime import datetime

# ArchE Framework Imports
from .workflow_engine import IARCompliantWorkflowEngine
from .action_registry import register_action, main_action_registry
from .utils.reflection_utils import create_reflection, ExecutionStatus
from .system_representation import System, GaussianDistribution, HistogramDistribution, StringParam
from .causal_inference_tool import perform_causal_inference
from .agent_based_modeling_tool import perform_abm
from .predictive_modeling_tool import run_prediction
from .llm_tool import generate_text_llm

logger = logging.getLogger(__name__)

@dataclass
class PerceptionFrame:
    """Represents a single frame of perception data with multi-modal inputs"""
    timestamp: float
    visual_features: Optional[Dict[str, Any]] = None
    audio_features: Optional[Dict[str, Any]] = None
    textual_content: Optional[str] = None
    sensor_data: Optional[Dict[str, float]] = None
    environmental_context: Optional[Dict[str, Any]] = None
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class PerceptionResult:
    """Results from perception processing"""
    interpretation: str
    confidence: float
    detected_patterns: List[Dict[str, Any]]
    causal_relationships: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    recommendations: List[str]
    risk_assessments: Dict[str, float]
    decision_framework: Dict[str, Any]
    iar_reflection: Dict[str, Any]

class ArchEPerceptionEngine:
    """
    Advanced multi-modal perception engine leveraging the full ArchE cognitive framework.
    Provides sophisticated environmental and informational understanding through:
    - Multi-modal data fusion and processing
    - Causal inference for understanding relationships
    - Predictive modeling for forecasting changes
    - Agent-based modeling for scenario simulation
    - Advanced workflow orchestration for complex perception tasks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the ArchE Perception Engine"""
        self.engine_id = f"arche_perception_{int(time.time())}"
        self.initialization_time = time.time()
        
        # Initialize core components
        self.workflow_engine = IARCompliantWorkflowEngine("workflows")
        self.perception_history: List[PerceptionFrame] = []
        self.system_state = System("PerceptionSystem", {
            "confidence_level": GaussianDistribution("confidence_level", mean=0.8, std=0.1),
            "processing_load": GaussianDistribution("processing_load", mean=0.5, std=0.2),
            "environmental_complexity": GaussianDistribution("environmental_complexity", mean=0.6, std=0.15),
            "threat_assessment": GaussianDistribution("threat_assessment", mean=0.1, std=0.05)
        })
        
        # Performance metrics
        self.performance_metrics = {
            "frames_processed": 0,
            "successful_interpretations": 0,
            "failed_interpretations": 0,
            "average_processing_time": 0.0,
            "accuracy_score": 0.0
        }
        
        # Register perception-specific actions
        self._register_perception_actions()
        
        logger.info(f"ArchE Perception Engine initialized with ID: {self.engine_id}")
    
    def _register_perception_actions(self):
        """Register perception-specific actions with the workflow engine"""
        register_action("process_perception_frame", self.process_perception_frame_action)
        register_action("analyze_patterns", self.analyze_patterns_action)
        register_action("predict_environmental_changes", self.predict_environmental_changes_action)
        register_action("assess_threats", self.assess_threats_action)
        register_action("generate_recommendations", self.generate_recommendations_action)
        register_action("fuse_multimodal_data", self.fuse_multimodal_data_action)
        
        # Update engine's action registry
        self.workflow_engine.action_registry = main_action_registry.actions.copy()
    
    def process_perception_frame_action(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Action wrapper for processing a single perception frame"""
        start_time = time.time()
        action_name = "process_perception_frame"
        
        try:
            # Extract frame data from inputs
            frame_data = inputs.get("frame_data", {})
            processing_mode = inputs.get("processing_mode", "comprehensive")
            
            # Create perception frame
            frame = PerceptionFrame(
                timestamp=frame_data.get("timestamp", time.time()),
                visual_features=frame_data.get("visual_features"),
                audio_features=frame_data.get("audio_features"),
                textual_content=frame_data.get("textual_content"),
                sensor_data=frame_data.get("sensor_data"),
                environmental_context=frame_data.get("environmental_context", {}),
                metadata=frame_data.get("metadata", {})
            )
            
            # Process the frame
            result = self._process_single_frame(frame, processing_mode)
            
            # Update system state based on processing results
            self._update_system_state(result)
            
            return {
                "perception_result": {
                    "interpretation": result.interpretation,
                    "confidence": result.confidence,
                    "patterns": result.detected_patterns,
                    "predictions": result.predictions,
                    "recommendations": result.recommendations
                },
                "system_metrics": self.get_performance_metrics(),
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.SUCCESS,
                    message=f"Successfully processed perception frame with {result.confidence:.2%} confidence",
                    inputs=inputs,
                    outputs={
                        "confidence": result.confidence,
                        "patterns_detected": len(result.detected_patterns),
                        "recommendations_count": len(result.recommendations)
                    },
                    confidence=result.confidence,
                    execution_time=time.time() - start_time
                )
            }
            
        except Exception as e:
            error_msg = f"Perception frame processing failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "error": error_msg,
                "reflection": create_reflection(
                    action_name=action_name,
                    status=ExecutionStatus.FAILURE,
                    message=error_msg,
                    inputs=inputs,
                    execution_time=time.time() - start_time
                )
            }
    
    def _process_single_frame(self, frame: PerceptionFrame, mode: str = "comprehensive") -> PerceptionResult:
        """Core perception processing logic for a single frame"""
        start_time = time.time()
        
        # Initialize result structure
        interpretation_parts = []
        confidence_scores = []
        detected_patterns = []
        causal_relationships = []
        predictions = {}
        recommendations = []
        risk_assessments = {}
        
        # Process visual features
        if frame.visual_features:
            visual_result = self._process_visual_features(frame.visual_features)
            interpretation_parts.append(f"Visual Analysis: {visual_result['interpretation']}")
            confidence_scores.append(visual_result['confidence'])
            detected_patterns.extend(visual_result.get('patterns', []))
            risk_assessments.update(visual_result.get('risks', {}))
        
        # Process audio features
        if frame.audio_features:
            audio_result = self._process_audio_features(frame.audio_features)
            interpretation_parts.append(f"Audio Analysis: {audio_result['interpretation']}")
            confidence_scores.append(audio_result['confidence'])
            detected_patterns.extend(audio_result.get('patterns', []))
            
            # Special handling for deception detection (Arche-AI style)
            if 'deception_indicators' in audio_result:
                risk_assessments['deception_risk'] = audio_result['deception_indicators']['risk_score']
                recommendations.append(f"Deception Risk: {audio_result['deception_indicators']['risk_level']}")
        
        # Process textual content
        if frame.textual_content:
            text_result = self._process_textual_content(frame.textual_content)
            interpretation_parts.append(f"Textual Analysis: {text_result['interpretation']}")
            confidence_scores.append(text_result['confidence'])
            detected_patterns.extend(text_result.get('patterns', []))
        
        # Process sensor data
        if frame.sensor_data:
            sensor_result = self._process_sensor_data(frame.sensor_data)
            interpretation_parts.append(f"Sensor Analysis: {sensor_result['interpretation']}")
            confidence_scores.append(sensor_result['confidence'])
            detected_patterns.extend(sensor_result.get('patterns', []))
            risk_assessments.update(sensor_result.get('risks', {}))
        
        # Perform causal inference if multiple data sources available
        if len([x for x in [frame.visual_features, frame.audio_features, frame.sensor_data] if x]) > 1:
            causal_result = self._perform_causal_analysis(frame)
            causal_relationships = causal_result.get('relationships', [])
            recommendations.extend(causal_result.get('recommendations', []))
        
        # Generate predictions using available data
        predictions = self._generate_predictions(frame, detected_patterns)
        
        # Create comprehensive interpretation
        overall_interpretation = ". ".join(interpretation_parts)
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        
        # Generate contextual recommendations
        context_recommendations = self._generate_contextual_recommendations(
            frame, detected_patterns, risk_assessments, predictions
        )
        recommendations.extend(context_recommendations)
        
        # Create decision framework
        decision_framework = {
            "primary_action": self._determine_primary_action(risk_assessments, predictions),
            "alternative_actions": self._generate_alternative_actions(detected_patterns),
            "confidence_threshold": 0.7,
            "requires_human_input": overall_confidence < 0.6 or max(risk_assessments.values(), default=0) > 0.7
        }
        
        # Create IAR reflection for the processing
        iar_reflection = create_reflection(
            action_name="perception_processing",
            status=ExecutionStatus.SUCCESS if overall_confidence > 0.5 else ExecutionStatus.PARTIAL,
            message=f"Processed perception frame with {len(detected_patterns)} patterns and {overall_confidence:.2%} confidence",
            inputs={"frame_timestamp": frame.timestamp, "processing_mode": mode},
            outputs={
                "patterns_count": len(detected_patterns),
                "confidence": overall_confidence,
                "risk_level": max(risk_assessments.values(), default=0.0)
            },
            confidence=overall_confidence,
            execution_time=time.time() - start_time
        )
        
        # Add frame to history
        self.perception_history.append(frame)
        
        # Update performance metrics
        self.performance_metrics["frames_processed"] += 1
        if overall_confidence > 0.7:
            self.performance_metrics["successful_interpretations"] += 1
        else:
            self.performance_metrics["failed_interpretations"] += 1
        
        return PerceptionResult(
            interpretation=overall_interpretation,
            confidence=overall_confidence,
            detected_patterns=detected_patterns,
            causal_relationships=causal_relationships,
            predictions=predictions,
            recommendations=recommendations,
            risk_assessments=risk_assessments,
            decision_framework=decision_framework,
            iar_reflection=iar_reflection
        )
    
    def _process_visual_features(self, visual_features: Dict[str, Any]) -> Dict[str, Any]:
        """Process visual perception data"""
        # Simulate advanced visual processing (would integrate with actual CV libraries)
        objects_detected = visual_features.get("objects", [])
        scene_description = visual_features.get("scene_description", "")
        
        patterns = []
        risks = {}
        
        # Object analysis
        if objects_detected:
            high_risk_objects = [obj for obj in objects_detected if obj.get("risk_level", 0) > 0.7]
            if high_risk_objects:
                risks["object_threat"] = max(obj.get("risk_level", 0) for obj in high_risk_objects)
                patterns.append({
                    "type": "high_risk_objects",
                    "count": len(high_risk_objects),
                    "objects": [obj["name"] for obj in high_risk_objects if "name" in obj]
                })
        
        # Scene analysis
        if scene_description:
            # Use LLM for advanced scene interpretation
            scene_analysis = self._analyze_with_llm(
                f"Analyze this visual scene for potential risks and patterns: {scene_description}",
                "scene_analysis"
            )
            if scene_analysis and not scene_analysis.get("error"):
                interpretation = scene_analysis.get("response", "Visual scene analyzed")
                confidence = 0.8
            else:
                interpretation = f"Visual scene contains {len(objects_detected)} detected objects"
                confidence = 0.6
        else:
            interpretation = f"Visual analysis of {len(objects_detected)} detected objects"
            confidence = 0.7
        
        return {
            "interpretation": interpretation,
            "confidence": confidence,
            "patterns": patterns,
            "risks": risks
        }
    
    def _process_audio_features(self, audio_features: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio perception data with deception detection"""
        # Simulate Arche-AI style audio processing
        audio_transcript = audio_features.get("transcript", "")
        voice_characteristics = audio_features.get("voice_characteristics", {})
        
        patterns = []
        deception_indicators = {
            "risk_score": 0.0,
            "risk_level": "low",
            "indicators": []
        }
        
        # Analyze transcript for deception indicators
        if audio_transcript:
            # Use LLM for sophisticated text analysis
            deception_analysis = self._analyze_with_llm(
                f"Analyze this audio transcript for potential deception indicators, inconsistencies, or concerning patterns. Consider linguistic patterns, contradictions, and emotional indicators: {audio_transcript}",
                "deception_analysis"
            )
            
            if deception_analysis and not deception_analysis.get("error"):
                response = deception_analysis.get("response", "")
                
                # Extract risk indicators from LLM response
                risk_keywords = ["high risk", "deceptive", "inconsistent", "suspicious", "concerning"]
                risk_score = sum(0.2 for keyword in risk_keywords if keyword in response.lower())
                risk_score = min(1.0, risk_score)  # Cap at 1.0
                
                deception_indicators = {
                    "risk_score": risk_score,
                    "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
                    "indicators": [indicator.strip() for indicator in response.split('.') if any(keyword in indicator.lower() for keyword in risk_keywords)][:3]
                }
                
                confidence = 0.85
                interpretation = f"Audio analysis reveals {deception_indicators['risk_level']} risk deception indicators"
            else:
                confidence = 0.6
                interpretation = "Audio transcript processed without advanced analysis"
        else:
            confidence = 0.5
            interpretation = "Audio features processed without transcript"
        
        # Voice characteristic analysis
        if voice_characteristics:
            patterns.append({
                "type": "voice_characteristics",
                "features": voice_characteristics
            })
        
        return {
            "interpretation": interpretation,
            "confidence": confidence,
            "patterns": patterns,
            "deception_indicators": deception_indicators
        }
    
    def _process_textual_content(self, content: str) -> Dict[str, Any]:
        """Process textual content for perception insights"""
        patterns = []
        
        # Use LLM for advanced text analysis
        text_analysis = self._analyze_with_llm(
            f"Perform comprehensive perception analysis on this text content. Identify key themes, potential risks, emotional indicators, and actionable insights: {content[:1000]}...",
            "text_perception_analysis"
        )
        
        if text_analysis and not text_analysis.get("error"):
            interpretation = text_analysis.get("response", "Text processed")
            confidence = 0.8
            
            # Extract patterns from LLM analysis
            response = text_analysis.get("response", "")
            if "pattern" in response.lower():
                patterns.append({
                    "type": "textual_patterns",
                    "analysis": response[:200] + "..." if len(response) > 200 else response
                })
        else:
            interpretation = f"Textual content analyzed: {len(content)} characters"
            confidence = 0.6
        
        return {
            "interpretation": interpretation,
            "confidence": confidence,
            "patterns": patterns
        }
    
    def _process_sensor_data(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """Process raw sensor data for environmental understanding"""
        patterns = []
        risks = {}
        
        # Analyze sensor readings for anomalies
        normal_ranges = {
            "temperature": (18.0, 25.0),
            "humidity": (30.0, 70.0),
            "pressure": (980.0, 1020.0),
            "light_level": (100.0, 1000.0),
            "sound_level": (30.0, 80.0),
            "motion_detected": (0.0, 1.0)
        }
        
        anomalies = []
        for sensor, value in sensor_data.items():
            if sensor in normal_ranges:
                min_val, max_val = normal_ranges[sensor]
                if not (min_val <= value <= max_val):
                    anomaly_severity = abs(value - np.mean([min_val, max_val])) / (max_val - min_val)
                    anomalies.append({
                        "sensor": sensor,
                        "value": value,
                        "expected_range": normal_ranges[sensor],
                        "severity": min(1.0, anomaly_severity)
                    })
        
        if anomalies:
            max_severity = max(a["severity"] for a in anomalies)
            risks["environmental_anomaly"] = max_severity
            patterns.append({
                "type": "sensor_anomalies",
                "count": len(anomalies),
                "max_severity": max_severity,
                "details": anomalies
            })
            interpretation = f"Sensor analysis detected {len(anomalies)} anomalies (max severity: {max_severity:.2f})"
            confidence = 0.9  # High confidence in sensor data
        else:
            interpretation = "All sensor readings within normal parameters"
            confidence = 0.85
        
        return {
            "interpretation": interpretation,
            "confidence": confidence,
            "patterns": patterns,
            "risks": risks
        }
    
    def _perform_causal_analysis(self, frame: PerceptionFrame) -> Dict[str, Any]:
        """Perform causal inference on multi-modal perception data"""
        try:
            # Create synthetic dataset from perception frame for causal analysis
            causal_data = self._frame_to_causal_data(frame)
            
            # Use ArchE causal inference tool
            causal_result = perform_causal_inference(
                operation="estimate_effect",
                data=causal_data,
                treatment="environmental_input",
                outcome="system_response",
                confounders=["context_factor"]
            )
            
            relationships = []
            recommendations = []
            
            if not causal_result.get("error"):
                effect_size = causal_result.get("causal_effect", 0.0)
                confidence_interval = causal_result.get("confidence_intervals", [0.0, 0.0])
                
                relationships.append({
                    "type": "environmental_response",
                    "effect_size": effect_size,
                    "confidence_interval": confidence_interval,
                    "strength": "strong" if abs(effect_size) > 0.5 else "moderate" if abs(effect_size) > 0.2 else "weak"
                })
                
                if abs(effect_size) > 0.5:
                    recommendations.append(f"Strong causal relationship detected (effect: {effect_size:.3f}) - consider adaptive response")
            
            return {
                "relationships": relationships,
                "recommendations": recommendations,
                "causal_analysis": causal_result
            }
            
        except Exception as e:
            logger.error(f"Causal analysis failed: {e}")
            return {"relationships": [], "recommendations": [], "error": str(e)}
    
    def _generate_predictions(self, frame: PerceptionFrame, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions about future environmental changes"""
        try:
            # Create time series data from perception history
            if len(self.perception_history) > 5:  # Need sufficient history
                prediction_data = self._history_to_prediction_data()
                
                # Use ArchE predictive modeling tool
                prediction_result = run_prediction(
                    operation="forecast",
                    data=prediction_data,
                    steps_to_forecast=5,
                    target_column="system_confidence"
                )
                
                if not prediction_result.get("error"):
                    forecast = prediction_result.get("forecast", [])
                    return {
                        "confidence_forecast": forecast,
                        "trend_direction": "increasing" if forecast[-1] > forecast[0] else "decreasing",
                        "prediction_confidence": 0.75,
                        "time_horizon": "5 frames"
                    }
            
            # Fallback to pattern-based predictions
            return self._pattern_based_predictions(patterns)
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return {"error": str(e), "fallback_predictions": True}
    
    def _generate_contextual_recommendations(self, frame: PerceptionFrame, 
                                           patterns: List[Dict[str, Any]], 
                                           risks: Dict[str, float],
                                           predictions: Dict[str, Any]) -> List[str]:
        """Generate context-aware recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        high_risks = {k: v for k, v in risks.items() if v > 0.7}
        if high_risks:
            recommendations.append(f"HIGH ALERT: {len(high_risks)} high-risk factors detected - immediate attention required")
            for risk_type, risk_value in high_risks.items():
                recommendations.append(f"Address {risk_type}: risk level {risk_value:.2%}")
        
        # Pattern-based recommendations
        pattern_types = [p["type"] for p in patterns]
        if "sensor_anomalies" in pattern_types:
            recommendations.append("Environmental monitoring recommended due to sensor anomalies")
        
        if "high_risk_objects" in pattern_types:
            recommendations.append("Enhanced surveillance and safety protocols advised")
        
        # Prediction-based recommendations
        if predictions.get("trend_direction") == "decreasing":
            recommendations.append("System performance trending downward - proactive maintenance suggested")
        
        return recommendations
    
    def _analyze_with_llm(self, prompt: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Use LLM for advanced analysis tasks"""
        try:
            llm_inputs = {
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.3,  # Lower temperature for analytical tasks
                "provider": "gemini"
            }
            
            result = generate_text_llm(llm_inputs)
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed for {analysis_type}: {e}")
            return None
    
    def _frame_to_causal_data(self, frame: PerceptionFrame) -> Dict[str, List]:
        """Convert perception frame to causal analysis dataset"""
        # Create synthetic causal dataset from frame data
        data = {
            "environmental_input": [1.0 if frame.visual_features or frame.sensor_data else 0.0],
            "system_response": [frame.confidence_scores.get("overall", 0.5)],
            "context_factor": [len(frame.environmental_context) / 10.0 if frame.environmental_context else 0.0]
        }
        
        # Add historical context if available
        if self.perception_history:
            recent_frames = self.perception_history[-5:]  # Last 5 frames
            for i, hist_frame in enumerate(recent_frames):
                data["environmental_input"].append(1.0 if hist_frame.visual_features or hist_frame.sensor_data else 0.0)
                data["system_response"].append(hist_frame.confidence_scores.get("overall", 0.5))
                data["context_factor"].append(len(hist_frame.environmental_context) / 10.0 if hist_frame.environmental_context else 0.0)
        
        return data
    
    def _history_to_prediction_data(self) -> Dict[str, List]:
        """Convert perception history to prediction dataset"""
        timestamps = []
        confidences = []
        
        for frame in self.perception_history[-20:]:  # Use last 20 frames
            timestamps.append(frame.timestamp)
            confidences.append(frame.confidence_scores.get("overall", 0.5))
        
        return {
            "timestamp": timestamps,
            "system_confidence": confidences
        }
    
    def _pattern_based_predictions(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions based on detected patterns"""
        predictions = {
            "environmental_stability": 0.7,  # Default assumption
            "threat_escalation_probability": 0.1,
            "system_performance_trend": "stable"
        }
        
        # Adjust predictions based on patterns
        high_risk_patterns = [p for p in patterns if p.get("type") in ["high_risk_objects", "sensor_anomalies"]]
        if high_risk_patterns:
            predictions["environmental_stability"] = 0.4
            predictions["threat_escalation_probability"] = 0.6
            predictions["system_performance_trend"] = "declining"
        
        return predictions
    
    def _determine_primary_action(self, risks: Dict[str, float], predictions: Dict[str, Any]) -> str:
        """Determine the primary recommended action"""
        max_risk = max(risks.values()) if risks else 0.0
        
        if max_risk > 0.8:
            return "immediate_intervention"
        elif max_risk > 0.5:
            return "enhanced_monitoring"
        elif predictions.get("threat_escalation_probability", 0) > 0.5:
            return "preventive_measures"
        else:
            return "continue_monitoring"
    
    def _generate_alternative_actions(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate alternative action options"""
        actions = ["maintain_current_state", "increase_sensor_sensitivity", "request_human_oversight"]
        
        # Add pattern-specific actions
        pattern_types = [p["type"] for p in patterns]
        if "sensor_anomalies" in pattern_types:
            actions.append("recalibrate_sensors")
        if "high_risk_objects" in pattern_types:
            actions.append("activate_safety_protocols")
        
        return actions
    
    def _update_system_state(self, result: PerceptionResult):
        """Update the internal system state based on perception results"""
        try:
            # Update system parameters based on perception results
            state_updates = {
                "confidence_level": (result.confidence, 0.05),  # (value, uncertainty)
                "processing_load": (min(1.0, len(result.detected_patterns) / 10.0), 0.1),
                "environmental_complexity": (len(result.detected_patterns) / 5.0, 0.1),
                "threat_assessment": (max(result.risk_assessments.values(), default=0.0), 0.05)
            }
            
            self.system_state.update_state(state_updates)
            
        except Exception as e:
            logger.error(f"System state update failed: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        total_processed = self.performance_metrics["frames_processed"]
        if total_processed > 0:
            success_rate = self.performance_metrics["successful_interpretations"] / total_processed
            self.performance_metrics["accuracy_score"] = success_rate
        
        return {
            **self.performance_metrics,
            "engine_uptime": time.time() - self.initialization_time,
            "system_state_summary": self.system_state.get_state()
        }
    
    def create_perception_workflow(self, workflow_name: str, perception_tasks: List[Dict[str, Any]]) -> str:
        """Create a custom perception workflow"""
        workflow_template = {
            "name": workflow_name,
            "description": "ArchE Perception Engine workflow for multi-modal environmental analysis",
            "version": "1.0",
            "perception_engine": True,
            "tasks": {}
        }
        
        # Add tasks to workflow
        for i, task in enumerate(perception_tasks):
            task_id = f"perception_task_{i+1}"
            workflow_template["tasks"][task_id] = {
                "description": task.get("description", f"Perception task {i+1}"),
                "action_type": task.get("action_type", "process_perception_frame"),
                "inputs": task.get("inputs", {}),
                "dependencies": task.get("dependencies", [])
            }
        
        # Save workflow
        workflow_path = Path("workflows") / f"{workflow_name}.json"
        with open(workflow_path, 'w') as f:
            json.dump(workflow_template, f, indent=2)
        
        logger.info(f"Created perception workflow: {workflow_path}")
        return str(workflow_path)
    
    async def process_continuous_stream(self, data_stream, processing_interval: float = 1.0):
        """Process continuous perception data stream"""
        logger.info("Starting continuous perception processing")
        
        try:
            async for frame_data in data_stream:
                # Process frame
                frame = PerceptionFrame(
                    timestamp=time.time(),
                    **frame_data
                )
                
                result = self._process_single_frame(frame)
                
                # Log significant events
                if result.confidence < 0.5:
                    logger.warning(f"Low confidence perception result: {result.confidence:.2%}")
                
                if max(result.risk_assessments.values(), default=0) > 0.7:
                    logger.critical(f"High risk detected: {result.risk_assessments}")
                
                # Wait for next processing interval
                await asyncio.sleep(processing_interval)
                
        except Exception as e:
            logger.error(f"Continuous processing error: {e}")

# Action wrapper functions for workflow integration
def create_perception_engine_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Create and initialize a perception engine instance"""
    start_time = time.time()
    
    try:
        config_path = inputs.get("config_path")
        engine = ArchEPerceptionEngine(config_path)
        
        return {
            "engine_id": engine.engine_id,
            "status": "initialized",
            "capabilities": [
                "multi_modal_processing",
                "causal_inference",
                "predictive_modeling", 
                "risk_assessment",
                "deception_detection"
            ],
            "reflection": create_reflection(
                action_name="create_perception_engine",
                status=ExecutionStatus.SUCCESS,
                message="Successfully initialized ArchE Perception Engine",
                inputs=inputs,
                outputs={"engine_id": engine.engine_id},
                confidence=1.0,
                execution_time=time.time() - start_time
            )
        }
        
    except Exception as e:
        error_msg = f"Perception engine creation failed: {str(e)}"
        return {
            "error": error_msg,
            "reflection": create_reflection(
                action_name="create_perception_engine",
                status=ExecutionStatus.FAILURE,
                message=error_msg,
                inputs=inputs,
                execution_time=time.time() - start_time
            )
        }

# Register the perception engine creation action
register_action("create_perception_engine", create_perception_engine_action)

if __name__ == "__main__":
    # Initialize and test the perception engine
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("=== ArchE Perception Engine Test ===")
    
    # Create test perception frame
    test_frame_data = {
        "visual_features": {
            "objects": [
                {"name": "person", "confidence": 0.95, "risk_level": 0.1},
                {"name": "vehicle", "confidence": 0.88, "risk_level": 0.3},
                {"name": "unknown_object", "confidence": 0.65, "risk_level": 0.8}
            ],
            "scene_description": "Urban environment with moderate traffic and pedestrian activity"
        },
        "audio_features": {
            "transcript": "Everything is fine here, no problems at all, definitely no issues",
            "voice_characteristics": {"stress_level": 0.7, "speaking_rate": 1.2}
        },
        "sensor_data": {
            "temperature": 22.5,
            "humidity": 45.0,
            "pressure": 1013.2,
            "sound_level": 95.0,  # Above normal range
            "motion_detected": 1.0
        },
        "environmental_context": {
            "location": "city_center",
            "time_of_day": "afternoon",
            "weather": "clear"
        }
    }
    
    # Initialize perception engine
    engine = ArchEPerceptionEngine()
    
    # Process test frame
    print("\\nProcessing test perception frame...")
    inputs = {
        "frame_data": test_frame_data,
        "processing_mode": "comprehensive"
    }
    
    result = engine.process_perception_frame_action(inputs)
    
    print("\\n=== Perception Results ===")
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        perception_result = result["perception_result"]
        print(f"Interpretation: {perception_result['interpretation']}")
        print(f"Confidence: {perception_result['confidence']:.2%}")
        print(f"Patterns Detected: {len(perception_result['patterns'])}")
        print(f"Recommendations: {len(perception_result['recommendations'])}")
        
        for i, rec in enumerate(perception_result['recommendations'][:3]):
            print(f"  {i+1}. {rec}")
    
    # Show performance metrics
    metrics = engine.get_performance_metrics()
    print(f"\\n=== Performance Metrics ===")
    print(f"Frames Processed: {metrics['frames_processed']}")
    print(f"Success Rate: {metrics['accuracy_score']:.2%}")
    print(f"Engine Uptime: {metrics['engine_uptime']:.2f} seconds")
    
    print("\\n=== Test Complete ===")