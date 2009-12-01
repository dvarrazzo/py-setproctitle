PTTEST_OBJS = pttest.o

PS_STATUS_URL = "http://git.postgresql.org/gitweb?p=postgresql.git;a=blob_plain;f=src/backend/utils/misc/ps_status.c;hb=HEAD"

CFLAGS = -g -Wall

CURL = wget -O -


all: pttest

pttest: $(PTTEST_OBJS)

ps_status.c :
	$(CURL) $(PS_STATUS_URL) > $@

