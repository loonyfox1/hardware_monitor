CC		:= g++
C_FLAGS := -std=c++17 -Wall -Wextra 

BIN		:= bin
SRC		:= src
INCLUDE	:= include -I/usr/include/qwt -I/usr/include/qt4/Qt -I/usr/include/qt4 -I/usr/include/qt4/QtGui
LIB		:= lib

LIBRARIES	:=

ifeq ($(OS),Windows_NT)
EXECUTABLE	:= main.exe
else
EXECUTABLE	:= main
endif

all: $(BIN)/$(EXECUTABLE)

clean:
	$(RM) $(BIN)/$(EXECUTABLE)

run: all
	./$(BIN)/$(EXECUTABLE)

$(BIN)/$(EXECUTABLE): $(SRC)/*
	$(CC) $(C_FLAGS) -I$(INCLUDE) -L$(LIB) $^ -o $@ $(LIBRARIES)