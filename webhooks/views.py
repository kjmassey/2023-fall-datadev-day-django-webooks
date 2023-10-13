import tableauserverclient as TSC
from rest_framework.viewsets import ModelViewSet
from webhooks.models import WebhookEvents
from webhooks.serializer import WebhookEventsSerializer
from rest_framework.decorators import action
from constants import PAT_NAME, PAT_SECRET, TSC_SERVER_URL, TSC_SITE_NAME
from rest_framework.response import Response
from rest_framework import status
from rest_framework import pagination


class ViewsetPaginator(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50
    page_query_param = "p"


class WebhookEventsViewset(ModelViewSet):
    queryset = WebhookEvents.objects.all().order_by("-created_at").values()
    serializer_class = WebhookEventsSerializer
    pagination_class = ViewsetPaginator

    def list(self, request):
        queryset = WebhookEvents.objects.all().order_by("-created_at").values()

        event_type = request.query_params.get("event_type")

        if event_type:
            vals = [val.strip() for val in event_type.split(",")]
            queryset = queryset.filter(event_type__in=vals)

        page = self.paginate_queryset(queryset)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WebhookEventsSerializer(queryset, many=True)

        return Response(serializer.data)


class WebhookActionsViewset(ModelViewSet):
    queryset = WebhookEvents.objects.all()
    serializer_class = WebhookEventsSerializer

    @action(methods=["POST"], detail=False)
    def delete_datasource(self, request):
        try:
            server = TSC.Server(TSC_SERVER_URL, use_server_version=True)
            tab_auth = TSC.PersonalAccessTokenAuth(
                PAT_NAME, PAT_SECRET, site_id=TSC_SITE_NAME
            )

            with server.auth.sign_in(tab_auth):
                server.datasources.delete(request.data.get("ds_luid"))

            return Response(
                {"success": f'Deleted datasource {request.data.get("ds_luid")}'},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "error": f"Couldn't delete datasource {request.data.get('ds_luid')}: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["POST"], detail=False)
    def delete_workbook(self, request):
        try:
            server = TSC.Server(TSC_SERVER_URL, use_server_version=True)
            tab_auth = TSC.PersonalAccessTokenAuth(
                PAT_NAME, PAT_SECRET, site_id=TSC_SITE_NAME
            )

            with server.auth.sign_in(tab_auth):
                server.workbooks.delete(request.data.get("wb_luid"))

            return Response(
                {"success": f'Deleted workbook {request.data.get("wb_luid")}'},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "error": f"Couldn't delete workbook {request.data.get('wb_luid')}: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["POST"], detail=False)
    def refresh_item(self, request):
        try:
            server = TSC.Server(TSC_SERVER_URL, use_server_version=True)
            tab_auth = TSC.PersonalAccessTokenAuth(
                PAT_NAME, PAT_SECRET, site_id=TSC_SITE_NAME
            )

            with server.auth.sign_in(tab_auth):
                obj_type = ""

                if request.data.get("event_type") == "WorkbookRefreshFailed":
                    obj_type = "workbook"
                    server.workbooks.refresh(request.data.get("luid"))

                else:
                    obj_type = "datasource"
                    server.datasources.refresh(request.data.get("luid"))

            return Response(
                {
                    "success": f'Refresh queued for {obj_type} {request.data.get("luid")}'
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "error": f"Couldn't create refresh job for {obj_type} {request.data.get('luid')}: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["POST"], detail=False)
    def remove_schedules(self, request):
        try:
            server = TSC.Server(TSC_SERVER_URL, use_server_version=True)
            tab_auth = TSC.PersonalAccessTokenAuth(
                PAT_NAME, PAT_SECRET, site_id=TSC_SITE_NAME
            )

            with server.auth.sign_in(tab_auth):
                tasks = list(TSC.Pager(server.tasks))
                filtered_tasks = list(
                    filter(lambda x: x.target.id == request.data.get("luid"), tasks)
                )

                for task in filtered_tasks:
                    server.tasks.delete(task.id)

                return Response(
                    {
                        "success": f"Deleted all schedule tasks for {request.data.get('luid')}"
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {
                    "error": f"Couldn't delete all schedule tasks for {request.data.get('luid')}: {str(e)}"
                },
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["POST"], detail=False)
    def add_tag(self, request):
        try:
            server = TSC.Server(TSC_SERVER_URL, use_server_version=True)
            tab_auth = TSC.PersonalAccessTokenAuth(
                PAT_NAME, PAT_SECRET, site_id=TSC_SITE_NAME
            )

            with server.auth.sign_in(tab_auth):
                if request.data.get("event_type") == "WorkbookRefreshFailed":
                    wb = server.workbooks.get_by_id(request.data.get("luid"))
                    wb.tags.add("Fails-Often")

                    server.workbooks.update(wb)

                else:
                    ds = server.datasources.get_by_id(request.data.get("luid"))
                    ds.tags.add("Fails-Often")

                    server.datasources.update(ds)

                return Response({"success": f"Added tag to {request.data.get('luid')}"})

        except Exception as e:
            return Response(
                {"error": f"Couldn't add tag to {request.data.get('luid')}: {str(e)}"}
            )
