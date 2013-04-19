<?
class CChecklist
{
        public function formatMoney($money)
        {
        return number_format($money, 2, ',', ' ');
    }
    
    public function checkPerm($permLevel)
        {
        global $APPLICATION;
        
        if($APPLICATION->GetGroupRight("checklist") >= $permLevel)
            return true;
        else
            return false;
    }

    public function getSnippet($string, $maxLength=150)
    {
        if(strlen($string) > $maxLength)
            return substr($string, 0, $maxLength) . '...';
        else
            return $string;
    }

    public function pluralForm($n, $form1, $form2, $form5)
    {
        $n = abs($n) % 100;
        $n1 = $n % 10;
        if ($n > 10 && $n < 20) return $form5;
        if ($n1 > 1 && $n1 < 5) return $form2;
        if ($n1 == 1) return $form1;
        return $form5;
    }

    public function mergeArrays($ar1, $ar2, $field1, $field2)
    {
        $result = $ar1;
        foreach ($ar1 as $key1 => &$val1) 
        {
            foreach ($ar2 as $key2 => &$val2) 
            {
                if($val1[$field1] === $val2[$field2])
                {
                    foreach ($val2 as $subKey => $subValue) {
                        $result[$key1][$subKey] = $subValue;
                    }
                    
                    break;
                }
            }
            
        }

        return $result;
    }
}
?>