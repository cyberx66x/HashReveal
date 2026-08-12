#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <dirent.h>
#include <unistd.h>
#include <ctype.h>

#define BASE_DIR "Passwords/Common-Credentials"
#define OUTPUT_FILE "all.txt"
#define MAX_PATH 1024
#define TABLE_SIZE 33554432 // 32 Million slots for ultra-fast hashing
#define NUM_LOCKS 4096      // Lock striping to prevent thread blocking

// Node for the Hash Table
typedef struct Node {
    char* word;
    struct Node* next;
} Node;

Node** hash_table;
pthread_mutex_t locks[NUM_LOCKS];

char** file_list;
int num_files = 0;
int current_file = 0;
pthread_mutex_t queue_lock;
unsigned long total_unique = 0;

// Fast string hashing algorithm (djb2)
unsigned long hash(const char *str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++))
        hash = ((hash << 5) + hash) + c;
    return hash;
}

// Thread-safe insert into the global hash table
void insert_word(const char* word) {
    unsigned long h = hash(word);
    unsigned long idx = h % TABLE_SIZE;
    unsigned long lock_idx = h % NUM_LOCKS;

    pthread_mutex_lock(&locks[lock_idx]);
    Node* current = hash_table[idx];
    
    // Check if word already exists
    while(current) {
        if (strcmp(current->word, word) == 0) {
            pthread_mutex_unlock(&locks[lock_idx]);
            return;
        }
        current = current->next;
    }
    
    // Insert new word
    Node* new_node = malloc(sizeof(Node));
    new_node->word = strdup(word);
    new_node->next = hash_table[idx];
    hash_table[idx] = new_node;
    
    // Update unique count (not strictly thread-safe without its own lock, but good enough for estimation, or we can count at the end)
    pthread_mutex_unlock(&locks[lock_idx]);
}

// Worker Thread Function
void* worker_thread(void* arg) {
    int thread_id = *(int*)arg;
    char filepath[MAX_PATH];
    char buffer[1024];

    while (1) {
        // Fetch the next file from the queue securely
        pthread_mutex_lock(&queue_lock);
        if (current_file >= num_files) {
            pthread_mutex_unlock(&queue_lock);
            break;
        }
        int f_idx = current_file++;
        strcpy(filepath, file_list[f_idx]);
        pthread_mutex_unlock(&queue_lock);

        printf("[Core %d] [%d/%d] Extracting words from: %s\n", thread_id, f_idx + 1, num_files, filepath);

        FILE* f = fopen(filepath, "r");
        if (!f) continue;

        while (fgets(buffer, sizeof(buffer), f)) {
            // Trim whitespace and newline
            char *p = buffer;
            while(*p && isspace((unsigned char)*p)) p++;
            char *end = p + strlen(p) - 1;
            while(end > p && isspace((unsigned char)*end)) *end-- = '\0';
            
            if (*p) {
                insert_word(p);
            }
        }
        fclose(f);
    }
    
    printf("[Core %d] Finished.\n", thread_id);
    return NULL;
}

int main() {
    printf("[*] Initializing High-Performance Hash Table...\n");
    
    hash_table = calloc(TABLE_SIZE, sizeof(Node*));
    for (int i = 0; i < NUM_LOCKS; i++) {
        pthread_mutex_init(&locks[i], NULL);
    }
    pthread_mutex_init(&queue_lock, NULL);

    // 1. Read Directory and Filter Files
    DIR *dir;
    struct dirent *ent;
    file_list = malloc(10000 * sizeof(char*)); // Assume max 10000 files

    if ((dir = opendir(BASE_DIR)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            if (ent->d_type == DT_REG) {
                char* name = ent->d_name;
                // Exclude generated hashes and output file
                if (strstr(name, "_MD5") || strstr(name, "_SHA") || strcmp(name, OUTPUT_FILE) == 0) {
                    continue;
                }
                char path[MAX_PATH];
                snprintf(path, sizeof(path), "%s/%s", BASE_DIR, name);
                file_list[num_files] = strdup(path);
                num_files++;
            }
        }
        closedir(dir);
    } else {
        perror("[-] Could not open directory");
        return EXIT_FAILURE;
    }

    printf("[*] Found %d wordlist files to process.\n", num_files);

    // 2. Launch Threads based on CPU Cores
    long num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (num_cores < 1) num_cores = 4; // Fallback
    printf("[*] Detected %ld CPU Cores. Utilizing maximum power...\n", num_cores);

    pthread_t threads[num_cores];
    int thread_ids[num_cores];

    for (int i = 0; i < num_cores; i++) {
        thread_ids[i] = i + 1;
        pthread_create(&threads[i], NULL, worker_thread, &thread_ids[i]);
    }

    // 3. Wait for all threads to complete
    for (int i = 0; i < num_cores; i++) {
        pthread_join(threads[i], NULL);
    }

    // 4. Write Unique Words to Output File
    printf("\n[*] All files processed! Writing unique words to %s...\n", OUTPUT_FILE);
    
    char out_path[MAX_PATH];
    snprintf(out_path, sizeof(out_path), "%s/%s", BASE_DIR, OUTPUT_FILE);
    FILE* out = fopen(out_path, "w");
    if (!out) {
        perror("[-] Failed to create output file");
        return EXIT_FAILURE;
    }

    for (unsigned long i = 0; i < TABLE_SIZE; i++) {
        Node* current = hash_table[i];
        while (current) {
            fprintf(out, "%s\n", current->word);
            total_unique++;
            Node* temp = current;
            current = current->next;
            free(temp->word); // Free memory
            free(temp);
        }
    }
    
    fclose(out);
    free(hash_table);
    
    printf("[+] Done! Successfully wrote %lu unique words to %s\n", total_unique, out_path);
    return EXIT_SUCCESS;
}