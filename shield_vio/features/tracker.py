"""OpenCV sparse feature frontend with persistent IDs and visual-health diagnostics."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - explicit optional dependency failure
    cv2 = None


@dataclass(frozen=True)
class VisualHealth:
    feature_count: int
    tracked_count: int
    new_count: int
    survival_rate: float
    outlier_ratio: float
    blur_variance: float
    mean_brightness: float


class FeatureTracker:
    def __init__(self, max_features: int = 300, min_distance_px: int = 12, quality_level: float = 0.01) -> None:
        if cv2 is None:
            raise ImportError("FeatureTracker requires opencv-python-headless")
        self.max_features=max_features; self.min_distance_px=min_distance_px; self.quality_level=quality_level
        self.prev_gray: np.ndarray | None=None; self.points=np.empty((0,1,2),np.float32); self.ids=np.empty(0,np.int64); self.ages=np.empty(0,np.int64); self.next_id=0

    def process(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray, VisualHealth]:
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) if image.ndim==3 else image.astype(np.uint8)
        old_n=len(self.points); outlier_ratio=0.0
        if self.prev_gray is not None and old_n:
            nxt,status,_=cv2.calcOpticalFlowPyrLK(self.prev_gray,gray,self.points,None,winSize=(21,21),maxLevel=3,
                                                  criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,0.01))
            back,bstatus,_=cv2.calcOpticalFlowPyrLK(gray,self.prev_gray,nxt,None,winSize=(21,21),maxLevel=3)
            fb=np.linalg.norm(self.points[:,0]-back[:,0],axis=1); keep=(status[:,0]>0)&(bstatus[:,0]>0)&(fb<1.5)
            outlier_ratio=float(1.0-np.mean(keep)) if old_n else 0.0
            self.points=nxt[keep].reshape(-1,1,2); self.ids=self.ids[keep]; self.ages=self.ages[keep]+1
        tracked=len(self.points)
        need=max(0,self.max_features-tracked); new_count=0
        if need:
            mask=np.full(gray.shape,255,np.uint8)
            for p in self.points[:,0].astype(int): cv2.circle(mask,tuple(p),self.min_distance_px,0,-1)
            new=cv2.goodFeaturesToTrack(gray,maxCorners=need,qualityLevel=self.quality_level,minDistance=self.min_distance_px,mask=mask,blockSize=7)
            if new is not None:
                new_count=len(new); new_ids=np.arange(self.next_id,self.next_id+new_count,dtype=np.int64); self.next_id+=new_count
                self.points=np.concatenate([self.points,new.astype(np.float32)]) if tracked else new.astype(np.float32)
                self.ids=np.concatenate([self.ids,new_ids]); self.ages=np.concatenate([self.ages,np.ones(new_count,dtype=np.int64)])
        blur=float(cv2.Laplacian(gray,cv2.CV_64F).var()); brightness=float(np.mean(gray))
        health=VisualHealth(len(self.points),tracked,new_count,float(tracked/old_n) if old_n else 1.0,outlier_ratio,blur,brightness)
        self.prev_gray=gray.copy(); return self.ids.copy(),self.points[:,0].copy(),health
