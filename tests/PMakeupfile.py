
echo("hello world")
for x in range(10):
    echo(x)

# this is a comment

def echo2(msg: str):
    echo(msg)
    echo(msg)

t = "hello"
echo(t)

y = cwd()
cd("tests")
z = cwd()
echo(y)
echo(z)

echo(list(ls()))

echo(list(ls_recursive("venv")))

echo2("boh")