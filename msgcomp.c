#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include "msgfile.h"

typedef struct {
    FILE *input;
    char *fname;
    int32_t num_lines;
    
    FILE *output;
    char *oname;
    int32_t cur_line, cur_offset;
} msgfile_compiler_ctx_t;

void write_int32_le(FILE *f, int32_t value) {
    fputc(value         & 0xFF, f);
    fputc((value >> 8)  & 0xFF, f);
    fputc((value >> 16) & 0xFF, f);
    fputc((value >> 24) & 0xFF, f);
}

msgfile_compiler_ctx_t *init_compiler_ctx(char *fname, char *oname) {
    msgfile_compiler_ctx_t *ctx = calloc(1, sizeof(msgfile_compiler_ctx_t));
    if (ctx == NULL) {
        fprintf(stderr, "MSGFILCMP-E-0000 Failed to allocate memory\n");
        return NULL;
    }
    
    ctx->input = fopen(fname, "rb");
    if (!ctx->input) {
        fprintf(
            stderr,
            "MSGFILCMP-E-0001 Error opening input file %s: %s\n",
            fname, strerror(errno)
        );
        free(ctx);
        return NULL;
    }
    
    ctx->num_lines = 0;
    char buf[256];
    int got_data = 0;
    char last_read = '\n';
    
    while (fgets(buf, sizeof(buf), ctx->input)) {
        size_t line_len = strlen(buf);
        
        if (line_len > 0) {
            got_data = 1;
            last_read = buf[line_len - 1];
            if (last_read == '\n') ctx->num_lines++;
        }
    }
    
    if (ferror(ctx->input)) {
        fprintf(
            stderr,
            "MSGFILCMP-E-0002 Error counting messages in input file %s: %s\n",
            fname, strerror(errno)
        );
        fclose(ctx->input);
        free(ctx);
        return NULL;
    }
    
    if (got_data && last_read != '\n') ctx->num_lines++;
    
    fseek(ctx->input, 0, SEEK_SET);
    
    if (ctx->num_lines > MSGFILE_MAX_MSG) {
        fprintf(
            stderr,
            "MSGFILCMP-E-0003 Too many messages in input file %s: ",
            fname
        );
        fprintf(stderr, "got %d, max %d\n", ctx->num_lines, MSGFILE_MAX_MSG);
        fclose(ctx->input);
        free(ctx);
        return NULL;
    }
    
    ctx->output = fopen(oname, "wb");
    if (!ctx->output) {
        fprintf(
            stderr,
            "MSGFILCMP-E-0004 Error opening output file %s: %s\n",
            oname, strerror(errno)
        );
        fclose(ctx->input);
        free(ctx);
        return NULL;
    }
    
    fprintf(
        stderr,
        "MSGFILCMP-I-0005 Compiling %d messages from %s to %s\n", 
        ctx->num_lines, fname, oname
    );
    
    ctx->fname = fname;
    ctx->oname = oname;
    ctx->cur_offset = (ctx->num_lines + 1) * 4;
    
    write_int32_le(ctx->output, ctx->num_lines);
    
    return ctx;
}

int main(int argc, char *argv[]) {
    msgfile_compiler_ctx_t *ctx = init_compiler_ctx(argv[1], argv[2]);
    if (ctx == NULL) {
        fprintf(stderr, "MSGFILCMP-F-000? Failed to initialize compiler\n");
        exit(EXIT_FAILURE);
    }
    
    return 0;
}