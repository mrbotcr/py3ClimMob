import argparse
import transaction
from pyramid.paster import get_appsettings, setup_logging
from climmob.config.encdecdata import encode_data_with_aes_key
from climmob.models import User
from climmob.models import get_engine, get_session_factory, get_tm_session
from climmob.models.meta import Base


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    args = parser.parse_args(raw_args)

    config_uri = args.ini_path

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, "climmob")

    enc_pass = encode_data_with_aes_key(
        settings.get("auth.root.password", "dbcchieg"), settings["aes.key"].encode()
    )

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)
    error = 0
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        try:
            dbsession.query(User).filter(User.user_name == "bioversity").update(
                {"user_password": enc_pass}
            )
        except Exception as e:
            print(str(e))
            error = 1
    engine.dispose()
    return error
