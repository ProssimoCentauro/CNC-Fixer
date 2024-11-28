#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int search_char(FILE *fd, char to_find)
{
    char c;
    c = fgetc(fd);
    while (c != EOF)
    {
        if (c == to_find)
            return (ftell(fd));
        c = fgetc(fd);
    }
    return (0);
}

float get_num(FILE *fd)
{
    char    c;
    char    *str;
    float num;
    size_t  i;

    c = fgetc(fd);
    str = (char *)malloc(7);
    i = 0;
    while (c != ' ')
    {
        str[i] = c;
        c = fgetc(fd);
        i++;
    }
    str[i] = '\0';
    num = strtof(str, NULL);
    free(str);
    return (num);
}

int main(int ac, char **av)
{
    if (ac != 2)
    {
        printf("not enough arguments!");
        return (0);
    }

    char path[512];

    #ifdef _WIN32
        strcpy(path, ".\\nc_file\\");
        strcat(path, av[1]);
    #else
        strcpy(path, "./nc_file/");
        strcat(path, av[1]);
    #endif

    FILE    *nc_file;
    float old_num_x;
    float old_num_y;
    float num_x;
    float num_y;
    int x_direction;
    int y_direction;
    int pos;

    nc_file = fopen(path, "r+");
    old_num_x = 0;
    old_num_y = 0;
    while (42)
    { 
        pos = search_char(nc_file, 'X');
        if (!pos)
            return (0);
        num_x = get_num(nc_file);
        if (old_num_x == 0)
        {
            old_num_x = num_x;
            x_direction = 1;
        }
        else if (num_x < old_num_x && x_direction == 1)
        {
            x_direction = -1;
            old_num_x = num_x;
            num_x += 0.01;
        }
        else if (num_x > old_num_x && x_direction == -1)
        {
            x_direction = 1;
            old_num_x = num_x;
            num_x += 0.01;
        }
        old_num_x = num_x;
        fseek(nc_file, pos, SEEK_SET);
        fprintf(nc_file, "%.3f", num_x);
    
        pos = search_char(nc_file, 'Y');
        if (!pos)
            return (0);
        num_y = get_num(nc_file);
        if (old_num_y == 0)
        {
            old_num_y = num_y;
            y_direction = 1;
        }
        else if (num_y < old_num_y && y_direction == 1)
        {
            y_direction = -1;
            old_num_y = num_y;
            num_y += 0.07;
        }
        else if (num_y > old_num_y && y_direction == -1)
        {
            y_direction = 1;
            old_num_y = num_y;
            num_y += 0.07;
        }
        old_num_y = num_y;
        fseek(nc_file, pos, SEEK_SET);
        fprintf(nc_file, "%.3f", num_y);
    }
    fclose(nc_file);
    return (0);
}
