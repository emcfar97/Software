students(0, []) :- !.
students(N, [(_Student,_Car,_Drink,_Sport,_Music)|T]) :- N1 is N-1, students(N1,T).

student(1, [H|_], H) :- !.
student(N, [_|T], R) :- N1 is N-1, student(N1, T, R).

% The Brit lives in a red house
hint1([(brit,red,_, _, _)|_]).
hint1([_|T]) :- hint1(T).
% The Swede keeps dogs as pets
hint2([(swede,_,_,_,dog)|_]).
hint2([_|T]) :- hint2(T).
% The Dane drinks tea
hint3([(dane,_,tea,_,_)|_]).
hint3([_|T]) :- hint3(T).
% The Green house is on the left of the White house
hint4([(_,green,_,_,_),(_,white,_,_,_)|_]).
hint4([_|T]) :- hint4(T).
% The owner of the Green house drinks coffee.
hint5([(_,green,coffee,_,_)|_]).
hint5([_|T]) :- hint5(T).
% The student who smokes Pall Mall rears birds
hint6([(_,_,_,pallmall,bird)|_]).
hint6([_|T]) :- hint6(T).
% The owner of the Yellow house smokes Dunhill
hint7([(_,yellow,_,dunhill,_)|_]).
hint7([_|T]) :- hint7(T).
% The man living in the centre house drinks milk
hint8(Students) :- student(3, Students, (_,_,milk,_,_)).
% The Norwegian lives in the first house
hint9(Students) :- student(1, Students, (norwegian,_,_,_,_)).
% The man who smokes Blends lives next to the one who keeps cats
hint10([(_,_,_,blend,_),(_,_,_,_,cat)|_]).
hint10([(_,_,_,_,cat),(_,_,_,blend,_)|_]).
hint10([_|T]) :- hint10(T).
% The man who keeps horses lives next to the man who smokes Dunhill
hint11([(_,_,_,dunhill,_),(_,_,_,_,horse)|_]).
hint11([(_,_,_,_,horse),(_,_,_,dunhill,_)|_]).
hint11([_|T]) :- hint11(T).
% The man who smokes Blue Master drinks beer
hint12([(_,_,beer,bluemaster,_)|_]).
hint12([_|T]) :- hint12(T).
% The German smokes Prince
hint13([(german,_,_,prince,_)|_]).
hint13([_|T]) :- hint13(T).
% The Norwegian lives next to the blue house
hint14([(norwegian,_,_,_,_),(_,blue,_,_,_)|_]).
hint14([(_,blue,_,_,_),(norwegian,_,_,_,_)|_]).
hint14([_|T]) :- hint14(T).
% The man who smokes Blends has a neighbour who drinks water
hint15([(_,_,_,blend,_),(_,_,water,_,_)|_]).
hint15([(_,_,water,_,_),(_,_,_,blend,_)|_]).
hint15([_|T]) :- hint15(T).
% The question : Who owns the fish ?
question([(_,_,_,_,fish)|_]).
question([_|T]) :- question(T).

question([(_,_,_,_,fish)|_]).
question([_|T]) :- question(T).

solution(Students) :-
  students(5, Students),
  hint1(Students),
  hint2(Students),
  hint3(Students),
  hint4(Students),
  hint5(Students),
  hint6(Students),
  hint7(Students),
  hint8(Students),
  hint9(Students),
  hint10(Students),
  hint11(Students),
  hint12(Students),
  hint13(Students),
  hint14(Students),
  hint15(Students),
  question(Students).










