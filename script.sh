FILES=test/*
for f in $FILES
   do
      output=`python Audio.py classify model $f | grep 'Classification'`
      echo "$f: $output"
   done

