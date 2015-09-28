# Create CSV files for every VBO file in the directory

vbosrcs = $(wildcard *.vbo)
csvdests = $(patsubst %.vbo,%.csv, $(vbosrcs))

all: csvs

csvs: $(csvdests)

clean:
	rm -f $(csvdests)

%.csv: %.vbo
	vboxread -c $@ $<
