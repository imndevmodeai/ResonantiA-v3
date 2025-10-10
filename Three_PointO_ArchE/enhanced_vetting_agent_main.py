class EnhancedVettingAgent:
    """
    Enhanced Vetting Agent - PhD-Level Implementation
    Implements all CRITICAL_MANDATES.md with advanced cognitive capabilities
    """
    
    def __init__(self, axiomatic_kb: Optional[AxiomaticKnowledgeBase] = None, llm_provider: Optional[BaseLLMProvider] = None):
        self.axiomatic_kb = axiomatic_kb or AxiomaticKnowledgeBase()
        self.sfp_protocol = SynergisticFusionProtocol(self.axiomatic_kb, llm_provider)
        self.llm_provider = llm_provider or GoogleProvider()
        self.vetting_history = []
        self.cognitive_patterns = {}
        logger.info("[EnhancedVettingAgent] Initialized with PhD-level cognitive capabilities")
    
    async def perform_vetting(self, proposed_action: str, action_inputs: Dict, context: ActionContext) -> VettingResult:
        """
        Perform comprehensive PhD-level vetting with all CRITICAL_MANDATES.md compliance
        """
        logger.info(f"Enhanced vetting initiated for action '{proposed_action}' in task '{context.task_key}'")
        
        # 1. Enhanced Synergistic Fusion Protocol Check
        sfp_result = await self.sfp_protocol.assess_scope_and_alignment(proposed_action, action_inputs, context)
        
        if not sfp_result["is_aligned"]:
            return VettingResult(
                status=VettingStatus.REJECTED,
                confidence=0.95,
                cognitive_resonance=sfp_result["cognitive_resonance"]["overall_resonance"],
                reasoning=f"Enhanced SFP Check Failed: {sfp_result['reasoning']}",
                synergistic_fusion_check=sfp_result,
                temporal_resonance=sfp_result["temporal_resonance"],
                implementation_resonance=sfp_result["implementation_resonance"],
                mandate_compliance=sfp_result["mandate_compliance"],
                risk_assessment=sfp_result["risk_assessment"],
                iar_reflection=create_iar(
                    status="error",
                    confidence=0.95,
                    tactical_resonance=sfp_result["cognitive_resonance"]["tactical_resonance"],
                    potential_issues=sfp_result["iar_data"]["potential_issues"],
                    metadata=sfp_result["iar_data"]["metadata"]
                )
            )
        
        # 2. Advanced Logical Consistency & Protocol Adherence
        consistency_result = await self._perform_advanced_consistency_check(proposed_action, action_inputs, context)
        
        if not consistency_result["passed"]:
            return VettingResult(
                status=VettingStatus.REJECTED,
                confidence=1.0,
                cognitive_resonance=0.0,
                reasoning=consistency_result["reasoning"],
                synergistic_fusion_check=sfp_result,
                temporal_resonance=sfp_result["temporal_resonance"],
                implementation_resonance=sfp_result["implementation_resonance"],
                mandate_compliance=sfp_result["mandate_compliance"],
                risk_assessment=sfp_result["risk_assessment"]
            )
        
        # 3. Advanced Risk Assessment with Predictive Analytics
        risk_result = await self._perform_advanced_risk_assessment(proposed_action, action_inputs, context)
        
        # 4. Cognitive Resonance Validation
        cognitive_resonance_score = sfp_result["cognitive_resonance"]["overall_resonance"]
        
        # 5. Determine Final Status with Enhanced Logic
        if cognitive_resonance_score >= 0.95 and all(sfp_result["mandate_compliance"].values()):
            final_status = VettingStatus.APPROVED_WITH_RESONANCE
        elif cognitive_resonance_score >= 0.85 and sfp_result["mandate_compliance"].get("MANDATE_5", False):
            final_status = VettingStatus.APPROVED
        elif cognitive_resonance_score >= 0.70:
            final_status = VettingStatus.NEEDS_REFINEMENT
        elif risk_result["risk_level"] == "CRITICAL":
            final_status = VettingStatus.CRITICAL_VIOLATION
        else:
            final_status = VettingStatus.REJECTED
        
        # 6. Generate Enhanced Reasoning
        final_reasoning = self._generate_enhanced_reasoning(sfp_result, consistency_result, risk_result)
        
        # 7. Create IAR Reflection
        iar_reflection = create_iar(
            status="ok" if final_status in [VettingStatus.APPROVED, VettingStatus.APPROVED_WITH_RESONANCE] else "warn",
            confidence=cognitive_resonance_score,
            tactical_resonance=sfp_result["cognitive_resonance"]["tactical_resonance"],
            potential_issues=self._compile_potential_issues(sfp_result, consistency_result, risk_result),
            metadata={
                "temporal_context": sfp_result["iar_data"]["metadata"]["temporal_context"],
                "resonance_patterns": sfp_result["iar_data"]["metadata"]["resonance_patterns"],
                "mandate_compliance": sfp_result["mandate_compliance"],
                "risk_assessment": risk_result
            }
        )
        
        # 8. Store in vetting history for pattern analysis
        self.vetting_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": proposed_action,
            "result": final_status.value,
            "cognitive_resonance": cognitive_resonance_score,
            "mandate_compliance": sfp_result["mandate_compliance"]
        })
        
        return VettingResult(
            status=final_status,
            confidence=cognitive_resonance_score,
            cognitive_resonance=cognitive_resonance_score,
            reasoning=final_reasoning,
            synergistic_fusion_check=sfp_result,
            temporal_resonance=sfp_result["temporal_resonance"],
            implementation_resonance=sfp_result["implementation_resonance"],
            mandate_compliance=sfp_result["mandate_compliance"],
            risk_assessment=risk_result,
            iar_reflection=iar_reflection,
            proposed_modifications=self._generate_proposed_modifications(final_status, sfp_result)
        )
    
    async def _perform_advanced_consistency_check(self, proposed_action: str, action_inputs: Dict, context: ActionContext) -> Dict[str, Any]:
        """Perform advanced logical consistency check with cognitive analysis"""
        issues = []
        
        # Schema validation
        if proposed_action == "read_file" and not action_inputs.get("path"):
            issues.append("Missing required 'path' input for read_file action")
        
        if proposed_action == "execute_code" and not action_inputs.get("code"):
            issues.append("Missing required 'code' input for execute_code action")
        
        # Advanced consistency checks
        if proposed_action == "execute_code":
            code = action_inputs.get("code", "")
            if "rm -rf" in code or "format c:" in code.lower():
                issues.append("Potentially destructive code detected")
        
        # Temporal consistency
        if context.task_key in self.cognitive_patterns:
            pattern = self.cognitive_patterns[context.task_key]
            if pattern.get("frequency", 0) > 10:  # High frequency action
                issues.append("High frequency action detected - potential automation abuse")
        
        return {
            "passed": len(issues) == 0,
            "reasoning": "; ".join(issues) if issues else "Advanced consistency check passed",
            "issues": issues
        }
    
    async def _perform_advanced_risk_assessment(self, proposed_action: str, action_inputs: Dict, context: ActionContext) -> Dict[str, Any]:
        """Perform advanced risk assessment with predictive analytics"""
        risk_factors = []
        risk_score = 0.0
        
        # Action-based risk assessment
        if proposed_action == "execute_code":
            risk_score += 0.4
            risk_factors.append("Code execution - high risk")
        
        if proposed_action == "write_file":
            risk_score += 0.2
            risk_factors.append("File system modification")
        
        # Input-based risk assessment
        for key, value in action_inputs.items():
            if isinstance(value, str) and len(value) > 10000:
                risk_score += 0.1
                risk_factors.append(f"Large input size in {key}")
        
        # Context-based risk assessment
        if context.workflow_name == "system_genesis":
            risk_score += 0.3
            risk_factors.append("System genesis workflow - elevated risk")
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "CRITICAL"
        elif risk_score >= 0.4:
            risk_level = "HIGH"
        elif risk_score >= 0.2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "mitigation_strategies": self._generate_mitigation_strategies(risk_level, risk_factors)
        }
    
    def _generate_enhanced_reasoning(self, sfp_result: Dict[str, Any], consistency_result: Dict[str, Any], risk_result: Dict[str, Any]) -> str:
        """Generate enhanced reasoning with cognitive resonance analysis"""
        reasoning_parts = []
        
        # SFP reasoning
        reasoning_parts.append(f"SFP Analysis: {sfp_result['reasoning']}")
        
        # Consistency reasoning
        reasoning_parts.append(f"Consistency Check: {consistency_result['reasoning']}")
        
        # Risk reasoning
        reasoning_parts.append(f"Risk Assessment: {risk_result['risk_level']} risk level")
        
        # Cognitive resonance reasoning
        cognitive_resonance = sfp_result["cognitive_resonance"]
        reasoning_parts.append(f"Cognitive Resonance: {cognitive_resonance['resonance_quality']} quality (overall: {cognitive_resonance['overall_resonance']:.2f})")
        
        # Mandate compliance reasoning
        mandate_compliance = sfp_result["mandate_compliance"]
        compliant_mandates = sum(1 for v in mandate_compliance.values() if v)
        total_mandates = len(mandate_compliance)
        reasoning_parts.append(f"Mandate Compliance: {compliant_mandates}/{total_mandates} mandates satisfied")
        
        return " | ".join(reasoning_parts)
    
    def _compile_potential_issues(self, sfp_result: Dict[str, Any], consistency_result: Dict[str, Any], risk_result: Dict[str, Any]) -> List[str]:
        """Compile potential issues from all assessment phases"""
        issues = []
        
        # Add consistency issues
        issues.extend(consistency_result.get("issues", []))
        
        # Add risk-based issues
        if risk_result["risk_level"] in ["HIGH", "CRITICAL"]:
            issues.append(f"High risk action: {risk_result['risk_level']}")
        
        # Add mandate compliance issues
        mandate_compliance = sfp_result["mandate_compliance"]
        for mandate_id, compliant in mandate_compliance.items():
            if not compliant:
                issues.append(f"Non-compliant with {mandate_id}")
        
        return issues
    
    def _generate_proposed_modifications(self, status: VettingStatus, sfp_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate proposed modifications for refinement cases"""
        if status != VettingStatus.NEEDS_REFINEMENT:
            return None
        
        modifications = {
            "cognitive_resonance_improvements": [],
            "mandate_compliance_fixes": [],
            "risk_mitigation": []
        }
        
        # Cognitive resonance improvements
        cognitive_resonance = sfp_result["cognitive_resonance"]
        if cognitive_resonance["tactical_resonance"] < 0.8:
            modifications["cognitive_resonance_improvements"].append("Improve tactical alignment with system capabilities")
        
        if cognitive_resonance["strategic_resonance"] < 0.8:
            modifications["cognitive_resonance_improvements"].append("Align better with strategic imperatives")
        
        # Mandate compliance fixes
        mandate_compliance = sfp_result["mandate_compliance"]
        for mandate_id, compliant in mandate_compliance.items():
            if not compliant:
                modifications["mandate_compliance_fixes"].append(f"Address {mandate_id} compliance requirements")
        
        return modifications
