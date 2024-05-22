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
    app.run(host="0.0.0.0")

    
