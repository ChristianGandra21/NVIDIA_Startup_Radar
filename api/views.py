from __future__ import annotations

import asyncio
from typing import Any

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import NvidiaRecommendations, Startups
from api.serializers import (
    NvidiaRecommendationsSerializer,
    StartupDetailSerializer,
    StartupListSerializer,
)


@api_view(["GET"])
def startup_list(request: Request) -> Response:
    qs = Startups.objects.all().prefetch_related(
        "classifications", "sources"
    )

    sector = request.query_params.get("sector")
    if sector:
        qs = qs.filter(sector__iexact=sector)

    ai_label = request.query_params.get("ai_label")
    if ai_label:
        qs = qs.filter(classifications__label__iexact=ai_label)

    funding = request.query_params.get("funding")
    if funding:
        qs = qs.filter(funding_stage__iexact=funding)

    state = request.query_params.get("state")
    if state:
        qs = qs.filter(state__iexact=state)

    search = request.query_params.get("q")
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(sector__icontains=search)
            | Q(description__icontains=search)
        )

    qs = qs.distinct()
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = StartupListSerializer(page if page is not None else qs, many=True)
    return paginator.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)


@api_view(["GET"])
def startup_detail(request: Request, pk: int) -> Response:
    try:
        startup = Startups.objects.prefetch_related(
            "classifications", "validations", "recommendations",
            "briefings", "sources",
        ).get(pk=pk)
    except Startups.DoesNotExist:
        return Response({"error": "Startup não encontrada"}, status=status.HTTP_404_NOT_FOUND)
    serializer = StartupDetailSerializer(startup)
    return Response(serializer.data)


@api_view(["POST"])
def startup_analyze(request: Request, pk: int) -> Response:
    try:
        startup = Startups.objects.get(pk=pk)
    except Startups.DoesNotExist:
        return Response({"error": "Startup não encontrada"}, status=status.HTTP_404_NOT_FOUND)

    from services.agents.graph import analyze_startup

    result: dict[str, Any] = asyncio.run(analyze_startup(startup.id))
    return Response({
        "startup_id": pk,
        "classification": {
            "label": result.get("ai_label"),
            "confidence": result.get("ai_confidence"),
        },
        "recommendations": [
            {"technology": r.get("technology"), "priority": r.get("priority")}
            for r in (result.get("recommendations") or [])
        ],
        "briefing": result.get("briefing", "")[:500] if result.get("briefing") else None,
    })


@api_view(["GET"])
def startup_search(request: Request) -> Response:
    query = request.query_params.get("q", "")
    if not query:
        return Response({"error": "Parâmetro 'q' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    from services.agents.planner import search_startups
    result = search_startups(query)
    startups = result.get("results", [])
    return Response({
        "query": query,
        "reason": result.get("plan", {}).get("reason", ""),
        "total": len(startups),
        "results": startups,
    })


@api_view(["GET"])
def startup_stats(request: Request) -> Response:
    total = Startups.objects.count()
    with_classification = Startups.objects.filter(classifications__isnull=False).distinct().count()
    ai_native = Startups.objects.filter(classifications__label="ai_native").distinct().count()
    ai_enabled = Startups.objects.filter(classifications__label="ai_enabled").distinct().count()
    non_ai = Startups.objects.filter(classifications__label="non_ai").distinct().count()

    sectors = (
        Startups.objects
        .values("sector")
        .annotate(count=Count("id"))
        .order_by("-count")[:20]
    )

    top_techs = (
        NvidiaRecommendations.objects
        .values("nvidia_technology")
        .annotate(count=Count("id"))
        .order_by("-count")[:20]
    )

    return Response({
        "total_startups": total,
        "classified": with_classification,
        "unclassified": total - with_classification,
        "by_ai_label": {
            "ai_native": ai_native,
            "ai_enabled": ai_enabled,
            "non_ai": non_ai,
        },
        "top_sectors": list(sectors),
        "top_recommended_technologies": list(top_techs),
    })
