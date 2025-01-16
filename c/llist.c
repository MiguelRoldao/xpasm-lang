
#include <stdlib.h>
#include <stdio.h>

#include "llist.h"

LElem
*lelem_new () {
	LElem *e = calloc(1, sizeof(*e));
	return e;
}

// destroy individual element
void
lelem_destroy (
	LElem *e
) {
	if (e == NULL) return;
	if (e->dtor) e->dtor(e->data);
	free (e);
}

// destroy whole list
void
lelem_exterminate (
	LElem *e
) {
	if (e == NULL) return;
	e = lelem_first(e);
	LElem *next;
	do {
		next = e->next;
		lelem_destroy(e);
		e = next;
	} while (e != NULL);
}


void
lelem_set (
	LElem *e,
	void *data,
	void (*dtor) (void*)
) {
	if (e == NULL) return;
	e->data = data;
	e->dtor = dtor;
}

LElem
*lelem_first (LElem *e) {
	if (e == NULL) return NULL;
	while (e->prev != NULL) e = e->prev;
	return e;
}

LElem
*lelem_last (LElem *e) {
	if (e == NULL) return NULL;
	while (e->next != NULL) e = e->next;
	return e;
}









LList
*llist_new () {
	LList *l = malloc(sizeof(*l));
	*l = NULL;
	return l;
}

void
llist_destroy (
	LList *l
) {
	if (*l) lelem_exterminate(*l);
	free(l);
}

void
llist_append (
	LList *l,
	LElem *e
) {
	if (l == NULL) {
		return;
	} else if (*l == NULL) {
		*l = e;
	} else {
		LElem *last = lelem_last(*l);
		last->next = e;
		e->prev = last;
		e->next = NULL;
	}
}

void
llist_insert (
	LList *l,
	LElem *e,
	int i
) {
	if (l == NULL || e == NULL) return;
	LElem *old = llist_get (l, i);
	if (old) {
		e->next = old;
		e->prev = old->prev;
		if (e->prev) {
			old->prev->next = e;
		}
		old->prev = e;
	} else if ((old = llist_get (l, i-1))) {
		e->next = NULL;
		e->prev = old;
		old->next = e;
	} else if (i == 0) {
		*l = e;
		e->next = NULL;
		e->prev = NULL;
	} else {
		// can't have a dangling element in a list
		return;
	}
}

void
llist_remove (
	LList *l,
	int i
) {
	LElem *e = llist_get(l, i);
	if (e == NULL) return;

	if (e->next) e->next->prev = e->prev;
	if (e->prev) e->prev->next = e->next;
	if (i == 0) *l = e->next;

	lelem_destroy(e);
}

LElem *llist_get (LList *l, int i) {
	LElem *e = *l;
	for (int j = 0; j < i && e != NULL; j++) {
		e = e->next;
	}
	return e;
}

int llist_length (LList *l) {
	if (l == NULL) return 0;
	int i = 0;
	LElem *e = *l;
	while (e != NULL) {
		i++;
		e = e->next;
	}
	return i;
}
