
#pragma once


typedef struct LElem LElem;
typedef LElem* LList;
struct LElem {
	LElem *next;
	LElem *prev;
	void *data;
	void (*dtor) (void*);
};

// []
LElem *lelem_new ();
void lelem_destroy (LElem *e);
void lelem_exterminate (LElem *e);

void lelem_set (LElem *e, void *data, void (*dtor) (void*));
LElem *lelem_last (LElem *e);
LElem *lelem_first (LElem *e);


LList *llist_new ();
void llist_destroy (LList *l);

void llist_append (LList *l, LElem *e);
void llist_insert (LList *l, LElem *e, int i);
void llist_remove (LList *l, int i);
LElem *llist_get (LList *l, int i);

int llist_length (LList *l);

