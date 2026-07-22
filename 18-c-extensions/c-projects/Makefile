PROJECTS := student-manager expense-tracker text-analyzer

.PHONY: all test sanitize clean

all:
	@for project in $(PROJECTS); do $(MAKE) -C $$project all || exit 1; done

test:
	@for project in $(PROJECTS); do $(MAKE) -C $$project test || exit 1; done

sanitize:
	@for project in $(PROJECTS); do $(MAKE) -C $$project sanitize || exit 1; done

clean:
	@for project in $(PROJECTS); do $(MAKE) -C $$project clean || exit 1; done

