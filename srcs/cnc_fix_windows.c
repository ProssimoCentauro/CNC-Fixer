#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int search_char(FILE *fd, char to_find)
{
    char c;
    int pos;

    while ((c = fgetc(fd)) != EOF)
    {
        if (c == to_find)
        {
            pos = ftell(fd) - 1; // Correggi la posizione per tornare al carattere trovato
            return pos;
        }
    }
    return 0; // Nessun carattere trovato
}

float get_num(FILE *fd)
{
    char c;
    size_t size = 16; // Dimensione iniziale del buffer
    char *str = (char *)malloc(size);
    if (!str)
    {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    size_t i = 0;

    while ((c = fgetc(fd)) != EOF && c != ' ' && c != '\n')
    {
        if (i >= size - 1) // Espandi il buffer se necessario
        {
            size *= 2;
            char *new_str = realloc(str, size);
            if (!new_str)
            {
                perror("Memory reallocation failed");
                free(str);
                exit(EXIT_FAILURE);
            }
            str = new_str;
        }
        str[i++] = c;
    }
    str[i] = '\0';

    float num = strtof(str, NULL);
    free(str);
    return num;
}

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <filename>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char path[512];

    // Creazione del percorso per Windows
    strcpy(path, ".\\nc_file\\");
    strcat(path, argv[1]);

    FILE *nc_file = fopen(path, "rb+");
    if (!nc_file)
    {
        perror("Error opening file");
        return EXIT_FAILURE;
    }

    float old_num_x = 0, old_num_y = 0;
    float num_x, num_y;
    int x_direction = 1, y_direction = 1;
    int pos;

    while (1)
    {
        // Gestione del carattere 'X'
        pos = search_char(nc_file, 'X');
        if (!pos)
            break;
        fseek(nc_file, pos + 1, SEEK_SET); // Posizionati dopo il carattere trovato
        num_x = get_num(nc_file);

        if (old_num_x == 0)
        {
            old_num_x = num_x;
        }
        else if (num_x < old_num_x && x_direction == 1)
        {
            x_direction = -1;
            num_x += 0.01;
        }
        else if (num_x > old_num_x && x_direction == -1)
        {
            x_direction = 1;
            num_x += 0.01;
        }
        old_num_x = num_x;

        fseek(nc_file, pos + 1, SEEK_SET);
        fprintf(nc_file, "%.3f", num_x);
        fflush(nc_file);

        // Gestione del carattere 'Y'
        pos = search_char(nc_file, 'Y');
        if (!pos)
            break;
        fseek(nc_file, pos + 1, SEEK_SET);
        num_y = get_num(nc_file);

        if (old_num_y == 0)
        {
            old_num_y = num_y;
        }
        else if (num_y < old_num_y && y_direction == 1)
        {
            y_direction = -1;
            num_y += 0.07;
        }
        else if (num_y > old_num_y && y_direction == -1)
        {
            y_direction = 1;
            num_y += 0.07;
        }
        old_num_y = num_y;

        fseek(nc_file, pos + 1, SEEK_SET);
        fprintf(nc_file, "%.3f", num_y);
        fflush(nc_file);
    }

    fclose(nc_file);
    return EXIT_SUCCESS;
}
