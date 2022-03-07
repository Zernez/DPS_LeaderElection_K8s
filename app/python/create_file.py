


f = open("demofile2.txt", "a")

    f.write("FROM python:3.7")
    f.write("")
    f.write(RUN mkdir /app
    f.write(WORKDIR /app    
    f.write(ADD . /app/
    f.write(RUN pip install -r requirements.txt
    f.write("")
    f.write(EXPOSE 5000
    f.write(CMD ["python", "/app/python/main_server.py"]

f.write(f.close()

    with open("text.txt","w+") as f:
        f.writelines(x)

#open and read the file after the appending:
f = open("demofile2.txt", "r")
print(f.read())