# import unittest
# from waitress import serve
# from app.main import create_app
# import logging

# app = create_app('dev')

# app.app_context().push()


# @app.cli.command()
# def test():
#     """Runs the unit tests."""
#     tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)

#     if result.wasSuccessful():
#         return 0
#     return 1


# if __name__ == "__main__":
#     logger = logging.getLogger('waitress')
#     logger.setLevel(logging.INFO)
#     serve(app, host='0.0.0.0', port=5000)


    
import unittest

from app.main import create_app

app = create_app('dev')

app.app_context().push()


@app.cli.command()
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

    
