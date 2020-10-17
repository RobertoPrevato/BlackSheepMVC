from blacksheep.server.openapi.v3 import serve_openapi_docs
from roconfiguration import Configuration
from rodi import Container

from blacksheep.server import Application
from blacksheep.server.files import ServeFilesOptions
from core.events import ServicesRegistrationContext

from . import controllers  # NoQA
from .auth import configure_authentication
from .errors import configure_error_handlers
from .templating import configure_templating
from .docs import docs


async def before_start(application: Application) -> None:
    application.services.add_instance(application)
    application.services.add_alias("app", Application)


async def after_start(application: Application) -> None:
    print(application.router.routes)


async def on_stop_1(application: Application) -> None:
    print(application.router.routes)


def configure_application(
    services: Container,
    context: ServicesRegistrationContext,
    configuration: Configuration,
) -> Application:
    app = Application(
        services=services,
        show_error_details=configuration.show_error_details,
        debug=configuration.debug,
    )

    app.on_start += before_start
    app.after_start += after_start
    app.on_stop += on_stop_1

    app.on_start += context.initialize
    app.on_stop += context.dispose

    configure_error_handlers(app)
    configure_authentication(app)
    configure_templating(app, configuration)

    app.serve_files(ServeFilesOptions("app/static"))

    serve_openapi_docs(app, docs)
    return app
