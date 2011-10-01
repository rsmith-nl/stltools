BEGIN {skip=0;}
/^\#beginskip/ {skip = 1;}
{if (skip == 0) print;}
/^\#endskip/ {skip = 0;}

