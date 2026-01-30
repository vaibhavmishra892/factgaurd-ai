"""
Fact Verification Orchestrator

This module coordinates all agents using CrewAI to verify factual claims.
NOW ONLY VERIFIES CLAIMS - input routing handled by input_router.py
"""

from crewai import Crew, Task, Process
from agents.planner_agent import create_planner_agent
from agents.finance_agent import create_finance_agent
from agents.news_agent import create_news_agent
from agents.consensus_agent import create_consensus_agent
from schemas.claim_schema import ClaimInput, RoutingDecision
from schemas.verdict_schema import VerdictResult, format_verdict_for_display
import json
import re

class FactVerifier:
    """Main orchestrator for fact verification using multi-agent system"""
    
    def __init__(self):
        """Initialize agents only (NO tools - routing handled externally)"""
        self.planner = create_planner_agent()
        self.finance_agent = create_finance_agent()
        self.news_agent = create_news_agent()
        self.consensus_agent = create_consensus_agent()
    
    def parse_routing_decision(self, planner_output: str) -> RoutingDecision:
        """
        Parse the Planner Agent's output to extract routing decision
        
        Args:
            planner_output: Raw output from Planner Agent
        
        Returns:
            RoutingDecision object
        """
        try:
            # Try to extract JSON from the output
            json_match = re.search(r'\{[^{}]*\}', planner_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return RoutingDecision(**data)
        except:
            pass
        
        # Fallback: parse from text
        intent = "general"
        time_sensitive = False
        required_agents = []
        reasoning = planner_output[:200]
        
        output_lower = planner_output.lower()
        
        # Detect intent
        if any(word in output_lower for word in ["stock", "price", "gold", "silver", "forex", "market", "financial"]):
            intent = "finance"
            required_agents.append("finance_agent")
        
        if any(word in output_lower for word in ["news", "announced", "reported", "article", "publication"]):
            if intent == "finance":
                intent = "mixed"
            else:
                intent = "news"
            required_agents.append("news_agent")
        
        # Detect time sensitivity
        if any(word in output_lower for word in ["yesterday", "today", "recent", "latest", "current", "now"]):
            time_sensitive = True
        
        return RoutingDecision(
            intent=intent,
            time_sensitive=time_sensitive,
            required_agents=list(set(required_agents)),
            reasoning=reasoning
        )
    
    
    def verify_claim(self, claim: str) -> str:
        """
        Main method to verify a factual text claim
        
        Args:
            claim: Clean text claim to verify (NO URLs, NO images - preprocessing done externally)
        
        Returns:
            Human-readable verification result
        """
        # Validate claim completeness BEFORE verification
        from tools.claim_validator import is_complete_claim, classify_claim_issue
        
        is_valid, reason = is_complete_claim(claim)
        if not is_valid:
            # Return friendly message, not harsh error
            return classify_claim_issue(claim)
        
        # Claim is valid - proceed with verification
        return self._verify_single_claim(claim)
    
    def verify_claims_batch(self, claims: list, source_info: dict = None, skip_validation: bool = False) -> str:
        """
        Verify multiple claims (e.g., from URL or image preprocessing)
        
        Args:
            claims: List of text claims to verify
            source_info: Optional metadata about the source
            skip_validation: If True, skip claim validation (for pre-validated/reconstructed claims)
            
        Returns:
            Aggregated verification results
        """
        if not claims:
            return "ℹ️ No valid claims found for verification.\n\nThe extracted content did not contain complete factual statements."
        
        # If skip_validation is True (e.g., for reconstructed image claims),
        # trust that they've been validated upstream
        if skip_validation:
            print(f"⏩ Skipping validation for {len(claims)} pre-validated/reconstructed claim(s)")
            valid_claims = claims
        else:
            # Validate all claims first
            from tools.claim_validator import is_complete_claim
            
            valid_claims = []
            invalid_count = 0
            
            for claim in claims:
                is_valid, reason = is_complete_claim(claim)
                if is_valid:
                    valid_claims.append(claim)
                else:
                    invalid_count += 1
            
            # If no valid claims after filtering
            if not valid_claims:
                return """ℹ️ The extracted text does not contain complete factual claims.

The content appears to contain sentence fragments or incomplete statements.

Please provide complete claims with clear subjects, actions, and context for verification."""
        
        results = []
        for i, claim in enumerate(valid_claims, 1):
            print(f"{'='*60}")
            print(f"Verifying Claim {i}/{len(claims)}")
            print(f"{'='*60}\n")
            result = self._verify_single_claim(claim)
            results.append({
                'claim': claim,
                'result': result
            })
        
        # Format aggregated results
        output = f"\n{'='*60}\n"
        if source_info:
            output += f"📰 MULTI-CLAIM VERIFICATION RESULTS\n"
            output += f"{'='*60}\n"
            output += f"Source: {source_info.get('source', 'Unknown')}\n"
            if 'title' in source_info:
                output += f"Title: {source_info['title']}\n"
            output += "\n"
        else:
            output += f"📊 BATCH VERIFICATION RESULTS\n"
            output += f"{'='*60}\n\n"
        
        for i, item in enumerate(results, 1):
            output += f"\n--- Claim {i} ---\n"
            output += f"Claim: {item['claim'][:100]}{'...' if len(item['claim']) > 100 else ''}\n"
            output += f"{item['result']}\n"
        
        return output
    
    def _verify_single_claim(self, claim: str) -> str:
        """
        Verify a single factual claim
        
        Args:
            claim: The factual claim to verify
        
        Returns:
            Human-readable verification result
        """
        
        # Step 1: Planning - Get routing decision
        print("🧠 Step 1: Analyzing claim and planning verification strategy...")
        
        planning_task = Task(
            description=f"""Analyze this claim and determine the verification strategy:
            
            Claim: "{claim}"
            
            You must output a JSON object with these fields:
            - intent: One of 'finance', 'news', 'events', 'mixed', or 'general'
            - time_sensitive: true or false
            - required_agents: List of agents to call (e.g., ['finance_agent', 'news_agent'])
            - reasoning: Brief explanation
            
            Example output:
            {{
                "intent": "finance",
                "time_sensitive": true,
                "required_agents": ["finance_agent", "news_agent"],
                "reasoning": "Claim involves recent financial data requiring both market data and news verification"
            }}
            """,
            agent=self.planner,
            expected_output="JSON object with routing decision"
        )
        
        planning_crew = Crew(
            agents=[self.planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=False
        )
        
        planner_output = planning_crew.kickoff()
        routing = self.parse_routing_decision(str(planner_output))
        
        print(f"📋 Routing Decision: {routing.intent} | Time-sensitive: {routing.time_sensitive}")
        print(f"🎯 Required agents: {routing.required_agents}")
        
        # Step 2: Intelligent Routing - Call only required agents
        evidence_collection = []
        agents_to_run = []
        verification_tasks = []
        
        if "finance_agent" in routing.required_agents:
            print("💰 Calling Finance Agent...")
            agents_to_run.append(self.finance_agent)
            
            finance_task = Task(
                description=f"""Verify this financial claim using market data:
                
                Claim: "{claim}"
                
                Use the Financial Data Fetcher tool to get relevant market data.
                Return your findings as structured evidence with source information.
                """,
                agent=self.finance_agent,
                expected_output="Financial evidence with source and data points"
            )
            verification_tasks.append(finance_task)
        
        if "news_agent" in routing.required_agents:
            print("📰 Calling News Agent...")
            agents_to_run.append(self.news_agent)
            
            news_task = Task(
                description=f"""Verify this claim using news sources and search:
                
                Claim: "{claim}"
                
                Use News Article Search and Google Search tools to find evidence.
                Prioritize trusted sources. Return findings with source credibility.
                """,
                agent=self.news_agent,
                expected_output="News evidence with source credibility and dates"
            )
            verification_tasks.append(news_task)
        
        # Execute verification tasks if any
        if verification_tasks:
            verification_crew = Crew(
                agents=agents_to_run,
                tasks=verification_tasks,
                process=Process.sequential,
                verbose=False
            )
            
            verification_output = verification_crew.kickoff()
            evidence_collection.append(str(verification_output))
        
        # Step 3: Consensus - Synthesize all evidence
        print("⚖️  Step 3: Building consensus and calculating confidence...")
        
        evidence_summary = "\n\n".join(evidence_collection) if evidence_collection else "No specific evidence gathered."
        
        consensus_task = Task(
            description=f"""Synthesize all evidence and produce final verdict:
            
            Original Claim: "{claim}"
            
            Routing Decision: {routing.reasoning}
            
            Evidence Collected:
            {evidence_summary}
            
            Your task:
            1. Review all evidence
            2. Check for contradictions
            3. Assess source credibility
            4. Calculate confidence score (0.0 to 1.0)
            5. Apply verdict rules:
               - confidence >= 0.8 → VERIFIED (if supports claim) or CONTRADICTED (if refutes claim)
               - 0.5 ≤ confidence < 0.8 → PARTIALLY TRUE
               - confidence < 0.5 → UNVERIFIABLE
            
            Output a clear summary with:
            - Verdict (VERIFIED/CONTRADICTED/PARTIALLY TRUE/UNVERIFIABLE)
            - Confidence score
            - Summary of findings
            - Evidence sources used
            - Any contradictions found
            - Additional notes
            """,
            agent=self.consensus_agent,
            expected_output="Final verdict with confidence, summary, and evidence sources"
        )
        
        consensus_crew = Crew(
            agents=[self.consensus_agent],
            tasks=[consensus_task],
            process=Process.sequential,
            verbose=False
        )
        
        consensus_output = consensus_crew.kickoff()
        
        # Step 4: Format output for UI
        print("✨ Step 4: Formatting results for display...")
        formatted_output = self._format_final_output(str(consensus_output), routing, evidence_collection)
        
        return formatted_output
    
    def _format_final_output(self, consensus_text: str, routing: RoutingDecision, evidence: list) -> str:
        """
        Format the consensus output into human-readable text
        
        Args:
            consensus_text: Raw output from Consensus Agent
            routing: Routing decision from Planner
            evidence: List of evidence strings
        
        Returns:
            Clean, formatted text for Gradio UI
        """
        
        # 1. Extract VERDICT (using regex)
        verdict = "CANNOT VERIFY"  # Fallback if absolutely no verdict found
        
        # Robust regex for Verdict
        verdict_pattern = r'(?:VERDICT|CONCLUSION|RESULT)[:\s\*]+(SUPPORTED|FALSE|CONTRADICTED|UNSUPPORTED|NOT FACTUAL|UNVERIFIABLE|CANNOT VERIFY|VERIFIED|PARTIALLY TRUE)'
        match = re.search(verdict_pattern, consensus_text, re.IGNORECASE)
        if match:
            found_verdict = match.group(1).upper()
            if found_verdict == "VERIFIED": verdict = "SUPPORTED"
            elif found_verdict == "PARTIALLY TRUE": verdict = "SUPPORTED"
            else: verdict = found_verdict

        # 2. Extract CONFIDENCE (using regex)
        confidence_str = "N/A"
        # Match "Confidence: High (0.95)" or "Confidence Score: 0.95" etc.
        # We want to capture the whole string "High (0.95)" or just "0.95" to display as-is if possible
        # But user wants "Confidence: <confidence>" so we can just extract the value/string
        
        # Try to find the confidence line
        conf_match = re.search(r'(?:CONFIDENCE|SCORE)[:\s\*]+(.+)', consensus_text, re.IGNORECASE)
        if conf_match:
            confidence_str = conf_match.group(1).strip()
        else:
            # Fallback: try to find just a number if line missing (less likely)
            num_match = re.search(r'([0-9]\.[0-9]+)', consensus_text)
            if num_match:
                confidence_str = num_match.group(1)

        # 3. Extract SUMMARY / EXPLANATION
        summary_text = "No summary provided."
        # Look for "Explanation:", "Summary:", "Summary of Findings:", or similar headers
        # Content is everything until "Sources:" or end of string
        
        # Regex to find the start of summary section - Longest matches FIRST
        summary_start_pattern = r'(?:SUMMARY OF FINDINGS|EXPLANATION|SUMMARY)[:\s\*]+'
        sources_start_pattern = r'(?:EVIDENCE SOURCES|SOURCES|REFERENCES)[:\s\*]+'
        
        split_by_summary = re.split(summary_start_pattern, consensus_text, flags=re.IGNORECASE)
        if len(split_by_summary) > 1:
            # The summary is the second part (index 1), but might contain Sources section
            # Note: split might return empty string at index 0 if match is at start
            summary_part = split_by_summary[1]
            
            # Split by Sources to isolate summary
            split_by_sources = re.split(sources_start_pattern, summary_part, flags=re.IGNORECASE)
            summary_text = split_by_sources[0].strip()
        else:
            # Fallback: extensive text that isn't verdict/confidence/sources
            # Strip verdict/confidence lines
            lines = consensus_text.split('\n')
            clean_lines = []
            for line in lines:
                if not re.search(verdict_pattern, line, re.IGNORECASE) and not re.search(r'(?:CONFIDENCE|SCORE)[:\s\*]+', line, re.IGNORECASE):
                    clean_lines.append(line)
            
            # Simple heuristic: first paragraph > 50 chars
            for p in "\n".join(clean_lines).split('\n\n'):
                 if len(p.strip()) > 50 and "Sources:" not in p and "SOURCES" not in p.upper():
                     summary_text = p.strip()
                     break

        # 4. Extract SOURCES
        sources_text = "No sources cited."
        # Split original text by sources pattern to capture it regardless of summary logic
        split_by_sources = re.split(sources_start_pattern, consensus_text, flags=re.IGNORECASE)
        if len(split_by_sources) > 1:
            sources_text = split_by_sources[1].strip()

            # Clean up if there are any trailing sections (unlikely based on prompt)
            # But sometimes "Additional Notes" might follow
            notes_pattern = r'(?:NOTES|ADDITIONAL NOTES)[:\s\*]+'
            split_by_notes = re.split(notes_pattern, sources_text, flags=re.IGNORECASE)
            if len(split_by_notes) > 1:
                sources_text = split_by_notes[0].strip()
        else:
             # Fallback to the keyword search ONLY if explicitly missing from text
             # But user said "Do NOT replace... evidence sources", so strictly we should output what's there
             # or say "No sources found in output" rather than inventing them
             pass 

        # 5. Construct Final Output Block
        final_output = []
        final_output.append("📊 VERIFICATION RESULT\n")
        final_output.append(f"Verdict: {verdict}")
        final_output.append(f"Confidence: {confidence_str}\n")
        
        final_output.append("Summary:")
        final_output.append(f"{summary_text}\n")
        
        final_output.append("Sources:")
        final_output.append(f"{sources_text}")
        
        return "\n".join(final_output)

# Create singleton instance
fact_verifier = FactVerifier()
