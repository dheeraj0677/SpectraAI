import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("telemetry")

class TelemetryManager:
    """Local, in-memory, privacy-safe telemetry and stage performance metrics store."""

    def __init__(self):
        self.start_time = time.time()
        self.total_jobs = 0
        self.failed_jobs = 0
        self.merge_conflicts_count = 0
        self.enrichment_hits_count = 0
        self.human_edits_count = 0
        self.stage_timings: Dict[str, List[float]] = {
            "ingestion": [],
            "extraction": [],
            "merging": [],
            "enrichment": [],
            "knowledge_graph": [],
            "validation": [],
            "total": []
        }

    def record_job_start(self):
        self.total_jobs += 1

    def record_job_failure(self):
        self.failed_jobs += 1

    def record_stage_timing(self, stage: str, duration_ms: float):
        if stage in self.stage_timings:
            self.stage_timings[stage].append(round(duration_ms, 2))
            # Retain last 100 observations to keep memory bound small
            if len(self.stage_timings[stage]) > 100:
                self.stage_timings[stage].pop(0)

    def record_conflict_found(self, count: int = 1):
        self.merge_conflicts_count += count

    def record_enrichment_hit(self, count: int = 1):
        self.enrichment_hits_count += count

    def record_human_edit(self, count: int = 1):
        self.human_edits_count += count

    def get_average_timing(self, stage: str) -> float:
        times = self.stage_timings.get(stage, [])
        if not times:
            return 0.0
        return round(sum(times) / len(times), 2)

    def get_diagnostics_snapshot(
        self,
        vlm_mode: str,
        graph_nodes: int,
        graph_edges: int,
        review_queue_size: int,
        approved_count: int
    ) -> Dict[str, Any]:
        uptime_seconds = round(time.time() - self.start_time, 1)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": uptime_seconds,
            "vlm_mode": vlm_mode,
            "pipeline_metrics": {
                "total_jobs_run": self.total_jobs,
                "failed_jobs_count": self.failed_jobs,
                "success_rate": f"{((self.total_jobs - self.failed_jobs) / self.total_jobs * 100):.1f}%" if self.total_jobs > 0 else "100.0%",
                "merge_conflicts_detected": self.merge_conflicts_count,
                "enrichment_hits_total": self.enrichment_hits_count,
                "human_edits_total": self.human_edits_count,
            },
            "average_stage_latencies_ms": {
                "ingestion": self.get_average_timing("ingestion"),
                "extraction": self.get_average_timing("extraction"),
                "merging": self.get_average_timing("merging"),
                "enrichment": self.get_average_timing("enrichment"),
                "knowledge_graph": self.get_average_timing("knowledge_graph"),
                "validation": self.get_average_timing("validation"),
                "total_pipeline": self.get_average_timing("total")
            },
            "catalog_and_graph_status": {
                "knowledge_graph_nodes": graph_nodes,
                "knowledge_graph_edges": graph_edges,
                "pending_review_queue": review_queue_size,
                "approved_products": approved_count
            }
        }

# Global singleton
telemetry = TelemetryManager()
