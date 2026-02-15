import math
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db
from app.crud import crud
from app.models.models import PlanItem, User
from app.schemas.schemas import (
    AddPlanItemResponse,
    OptimizePlanResponse,
    PlanConflictWarning,
    PlanItemCreate,
    PlanItemResponse,
    PlanItemUpdate,
    UserPlanCreate,
    UserPlanResponse,
    UserPlanUpdate,
)

router = APIRouter()


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def _conflict_warnings(items: List[PlanItem]) -> List[PlanConflictWarning]:
    warnings: List[PlanConflictWarning] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            left = items[i]
            right = items[j]
            if _overlaps(left.desired_time_start, left.desired_time_end, right.desired_time_start, right.desired_time_end):
                warnings.append(
                    PlanConflictWarning(
                        item_id=left.id,
                        conflict_with_item_id=right.id,
                        detail="Solape detectado entre ventanas horarias.",
                    )
                )
    return warnings


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


@router.get("/me/plans", response_model=List[UserPlanResponse])
def list_my_plans(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.list_user_plans(db, user_id=current_user.id, from_date=from_date, to_date=to_date)


@router.post("/me/plans", response_model=UserPlanResponse, status_code=201)
def create_plan(
    payload: UserPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.create_user_plan(db, user_id=current_user.id, title=payload.title, plan_date=payload.plan_date)


@router.get("/me/plans/{plan_id}", response_model=UserPlanResponse)
def get_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.patch("/me/plans/{plan_id}", response_model=UserPlanResponse)
def patch_plan(
    plan_id: str,
    payload: UserPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return crud.update_user_plan(db, plan=plan, title=payload.title, plan_date=payload.plan_date)


@router.post("/me/plans/{plan_id}/items", response_model=AddPlanItemResponse, status_code=201)
def create_item(
    plan_id: str,
    payload: PlanItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    item = crud.create_plan_item(
        db,
        plan_id=plan.id,
        item_type=payload.item_type.value,
        event_id=payload.event_id,
        brotherhood_id=payload.brotherhood_id,
        desired_time_start=payload.desired_time_start,
        desired_time_end=payload.desired_time_end,
        lat=payload.lat,
        lng=payload.lng,
        notes=payload.notes,
    )

    refreshed = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan.id)
    warnings = _conflict_warnings(refreshed.items)
    return AddPlanItemResponse(item=PlanItemResponse.model_validate(item), warnings=warnings)


@router.patch("/me/plans/{plan_id}/items/{item_id}", response_model=AddPlanItemResponse)
def patch_item(
    plan_id: str,
    item_id: str,
    payload: PlanItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    item = crud.get_plan_item(db, plan_id=plan_id, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Plan item not found")

    new_start = payload.desired_time_start or item.desired_time_start
    new_end = payload.desired_time_end or item.desired_time_end
    if new_start > new_end:
        raise HTTPException(status_code=422, detail="desired_time_start must be <= desired_time_end")

    updated = crud.update_plan_item(
        db,
        item=item,
        desired_time_start=payload.desired_time_start,
        desired_time_end=payload.desired_time_end,
        lat=payload.lat,
        lng=payload.lng,
        notes=payload.notes,
    )
    refreshed = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan.id)
    warnings = _conflict_warnings(refreshed.items)
    return AddPlanItemResponse(item=PlanItemResponse.model_validate(updated), warnings=warnings)


@router.delete("/me/plans/{plan_id}/items/{item_id}", status_code=204)
def remove_item(
    plan_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    item = crud.get_plan_item(db, plan_id=plan_id, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Plan item not found")
    crud.delete_plan_item(db, item=item)
    return None


@router.post("/me/plans/{plan_id}/optimize", response_model=OptimizePlanResponse)
def optimize_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = crud.get_user_plan(db, user_id=current_user.id, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    items = sorted(plan.items, key=lambda item: item.desired_time_start)
    if not items:
        return OptimizePlanResponse(items=[], warnings=[])

    ordered = [items[0]]
    remaining = items[1:]

    while remaining:
        current = ordered[-1]
        if current.lat is None or current.lng is None:
            next_item = remaining.pop(0)
            ordered.append(next_item)
            continue

        next_item = min(
            remaining,
            key=lambda candidate: _haversine(
                current.lat,
                current.lng,
                candidate.lat if candidate.lat is not None else current.lat,
                candidate.lng if candidate.lng is not None else current.lng,
            ),
        )
        remaining.remove(next_item)
        ordered.append(next_item)

    reordered = crud.reorder_plan_items(db, plan_id=plan.id, ordered_ids=[item.id for item in ordered])
    warnings = _conflict_warnings(reordered)
    return OptimizePlanResponse(items=[PlanItemResponse.model_validate(item) for item in reordered], warnings=warnings)
