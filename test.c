
#include <stdio.h>

int main()
{
	printf("hello %d", 12);
	char *p = (char *)0x7650cc28;
	char one = p[0];
	char two = p[1];
	char three = p[2];

	printf("%c, %c, %c", one, two, three);

	return 0;

}

