:- use_module(library(clpfd)).

write_to_file(File, Text) :-
    open(File, write, Stream),
    write(Stream, Text), nl,
    close(Stream).

neighbors(X, Y) :-
    (X #= (Y - 1)) #\/ (X #= (Y + 1)).

solve(ZebraOwner) :-
    maplist( init_dom(1..5),
        [[Accounting, Computer_science, Engineering, History, English],  % Majors
         [Ford, Chevy, Nissan, Toyota, Tesla],     % Cars
         [Royals, Chiefs, Yankees, Broncos, Cubs], % Sports
         [Classical, Country, Jazz, Rock, Techno], % Fan
         [Coke, Coffee, Tea, Milk, Water]]),       % Drinks

    Computer_science #= __,   % Hint 1
    History #= Jazz,           % Hint 2
    Yankees #= Toyota,         % Hint 3
    Accounting #= Coke,        % Hint 4
    Engineering #= Coffee,     % Hint 5
    neighbors(Computer_science, History), % Hint 6
    __ #= Classical,           % Hint 7
    Tea #= Tesla,              % Hint 8
    neighbors(Classical, Jazz),% Hint 9
    __,             % Hint 10
    Royals #= Tesla,           % Hint 11
    Cubs #= Jazz,              % Hint 12
    Engineering #= Chiefs,     % Hint 13
    __ #= Broncos, % Hint 14
    Coke #= Nissan,            % Hint 15
    neighbors(Country, Techno),% Hint 16
    Accounting #= __,         % Hint 17
    neighbors(Chiefs, Royals), % Hint 18
    Accounting #= Rock,        % Hint 19
    Yankees #= Milk,           % Hint 20
    Chevy #= Country,          % Hint 21
    Jazz #= Ford,              % Hint 22

    memberchk(Zebra-ZebraOwner, [Computer_science-computer_science, History-history, Yankees-yankees, Classical-classical]
             ).

init_dom(R, L) :-
    all_distinct(L),
    L ins R.
