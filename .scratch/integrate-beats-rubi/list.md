# Entries native integrate passes and rubi fails

1203 entries over classes 1, 2, 3, 4, 5, 6, 7, 8. Baseline `test/corpus_classN.baseline.out` (native integrate, 30 s wall cap) against `test/corpus_classN.out` (rubi, 30 s cpu cap), compared with `test/ab_records.py`. Regenerate with `python3 .scratch/integrate-beats-rubi/collect.py > .scratch/integrate-beats-rubi/list.md`.

| class | entries | rubi failure classes |
|---|---|---|
| 1 | 720 | contains-noun 400, timeout 263, deferred 27, unverified 27, error 3 |
| 2 | 22 | contains-noun 10, deferred 10, timeout 2 |
| 3 | 66 | timeout 46, contains-noun 19, unexpected 1 |
| 4 | 158 | contains-noun 91, unverified 32, timeout 29, deferred 4, error 2 |
| 5 | 108 | contains-noun 91, timeout 12, deferred 5 |
| 6 | 61 | contains-noun 44, timeout 8, unverified 8, deferred 1 |
| 7 | 41 | contains-noun 30, timeout 10, error 1 |
| 8 | 27 | contains-noun 27 |

## Class 1 (720)

### rubi contains-noun (400)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 1.1.1.2 (a+b x)^m (c+d x)^n | e756 | verified 0.1s | 1.4s | `x^3*(a+b*x)*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e757 | verified 0.1s | 1.4s | `x^2*(a+b*x)*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e758 | verified 0.1s | 0.9s | `x*(a+b*x)*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e759 | verified 0.1s | 0.5s | `(a+b*x)*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e760 | verified 0.1s | 1.4s | `(a+b*x)*sqrt(c*x^2)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e761 | verified 0.1s | 1.4s | `(a+b*x)*sqrt(c*x^2)/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e762 | verified 0.1s | 2.0s | `(a+b*x)*sqrt(c*x^2)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e763 | expected 0.1s | 2.1s | `(a+b*x)*sqrt(c*x^2)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e764 | verified 0.1s | 1.5s | `x^3*(c*x^2)^(3/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e765 | verified 0.1s | 1.4s | `x^2*(c*x^2)^(3/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e766 | verified 0.1s | 1.4s | `x*(c*x^2)^(3/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e767 | verified 0.1s | 1.5s | `(c*x^2)^(3/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e768 | verified 0.1s | 0.9s | `(c*x^2)^(3/2)*(a+b*x)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e769 | verified 0.1s | 0.5s | `(c*x^2)^(3/2)*(a+b*x)/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e770 | verified 0.1s | 1.9s | `(c*x^2)^(3/2)*(a+b*x)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e771 | verified 0.1s | 2.2s | `(c*x^2)^(3/2)*(a+b*x)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e772 | verified 0.1s | 1.3s | `x^3*(c*x^2)^(5/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e773 | verified 0.1s | 1.4s | `x^2*(c*x^2)^(5/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e774 | verified 0.1s | 1.4s | `x*(c*x^2)^(5/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e775 | verified 0.1s | 1.4s | `(c*x^2)^(5/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e776 | verified 0.1s | 1.4s | `(c*x^2)^(5/2)*(a+b*x)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e777 | verified 0.1s | 1.4s | `(c*x^2)^(5/2)*(a+b*x)/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e778 | verified 0.1s | 1.2s | `(c*x^2)^(5/2)*(a+b*x)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e779 | verified 0.1s | 0.6s | `(c*x^2)^(5/2)*(a+b*x)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e780 | verified 0.1s | 0.9s | `x^3*(a+b*x)/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e781 | verified 0.1s | 0.6s | `x^2*(a+b*x)/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e782 | verified 0.1s | 1.4s | `x*(a+b*x)/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e783 | verified 0.1s | 1.0s | `(a+b*x)/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e784 | verified 0.1s | 2.9s | `(a+b*x)/(x*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e785 | expected 0.1s | 3.4s | `(a+b*x)/(x^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e786 | verified 0.1s | 3.0s | `(a+b*x)/(x^3*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e787 | verified 0.1s | 3.0s | `(a+b*x)/(x^4*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e788 | verified 0.1s | 1.3s | `x^3*(a+b*x)/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e789 | verified 0.1s | 1.1s | `x^2*(a+b*x)/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e790 | verified 0.1s | 3.1s | `x*(a+b*x)/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e791 | expected 0.1s | 3.5s | `(a+b*x)/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e792 | verified 0.1s | 3.5s | `(a+b*x)/(x*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e793 | verified 0.1s | 3.4s | `(a+b*x)/(x^2*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e794 | verified 0.1s | 3.5s | `(a+b*x)/(x^3*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e795 | verified 0.1s | 3.5s | `(a+b*x)/(x^4*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e796 | verified 0.1s | 3.6s | `x^3*(a+b*x)/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e797 | expected 0.1s | 3.8s | `x^2*(a+b*x)/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e798 | verified 0.1s | 3.8s | `x*(a+b*x)/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e799 | verified 0.1s | 4.1s | `(a+b*x)/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e800 | verified 0.1s | 3.7s | `(a+b*x)/(x*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e801 | verified 0.1s | 3.9s | `(a+b*x)/(x^2*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e802 | verified 0.1s | 3.9s | `(a+b*x)/(x^3*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e803 | verified 0.1s | 3.9s | `(a+b*x)/(x^4*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e804 | verified 0.1s | 2.3s | `x^3*(a+b*x)^2*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e805 | verified 0.1s | 2.5s | `x^2*(a+b*x)^2*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e806 | verified 0.1s | 1.6s | `x*(a+b*x)^2*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e807 | verified 0.1s | 0.9s | `(a+b*x)^2*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e808 | expected 0.1s | 2.1s | `(a+b*x)^2*sqrt(c*x^2)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e809 | verified 0.1s | 1.7s | `(a+b*x)^2*sqrt(c*x^2)/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e810 | verified 0.1s | 2.7s | `(a+b*x)^2*sqrt(c*x^2)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e811 | verified 0.1s | 2.8s | `(a+b*x)^2*sqrt(c*x^2)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e812 | verified 0.1s | 2.3s | `x^3*(c*x^2)^(3/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e813 | verified 0.1s | 2.3s | `x^2*(c*x^2)^(3/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e814 | verified 0.1s | 2.6s | `x*(c*x^2)^(3/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e815 | verified 0.1s | 2.3s | `(c*x^2)^(3/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e816 | verified 0.1s | 1.8s | `(c*x^2)^(3/2)*(a+b*x)^2/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e817 | verified 0.1s | 0.8s | `(c*x^2)^(3/2)*(a+b*x)^2/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e818 | expected 0.1s | 2.9s | `(c*x^2)^(3/2)*(a+b*x)^2/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e819 | verified 0.1s | 3.0s | `(c*x^2)^(3/2)*(a+b*x)^2/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e820 | verified 0.1s | 2.3s | `x*(c*x^2)^(5/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e821 | verified 0.1s | 2.4s | `(c*x^2)^(5/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e822 | verified 0.1s | 2.3s | `(c*x^2)^(5/2)*(a+b*x)^2/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e823 | verified 0.1s | 2.3s | `(c*x^2)^(5/2)*(a+b*x)^2/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e824 | verified 0.1s | 1.7s | `(c*x^2)^(5/2)*(a+b*x)^2/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e825 | verified 0.1s | 0.8s | `(c*x^2)^(5/2)*(a+b*x)^2/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e826 | expected 0.1s | 2.9s | `(c*x^2)^(5/2)*(a+b*x)^2/x^5` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e827 | verified 0.1s | 2.6s | `(c*x^2)^(5/2)*(a+b*x)^2/x^6` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e828 | verified 0.1s | 1.5s | `x^3*(a+b*x)^2/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e829 | verified 0.1s | 1.0s | `x^2*(a+b*x)^2/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e830 | expected 0.1s | 2.5s | `x*(a+b*x)^2/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e831 | verified 0.1s | 1.4s | `(a+b*x)^2/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e832 | verified 0.1s | 3.8s | `(a+b*x)^2/(x*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e833 | verified 0.1s | 3.9s | `(a+b*x)^2/(x^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e834 | expected 0.1s | 3.8s | `(a+b*x)^2/(x^3*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e835 | verified 0.1s | 3.8s | `(a+b*x)^2/(x^4*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e836 | expected 0.1s | 2.4s | `x^3*(a+b*x)^2/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e837 | verified 0.1s | 1.4s | `x^2*(a+b*x)^2/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e838 | verified 0.1s | 3.9s | `x*(a+b*x)^2/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e839 | verified 0.1s | 3.6s | `(a+b*x)^2/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e840 | expected 0.1s | 3.8s | `(a+b*x)^2/(x*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e841 | verified 0.1s | 3.8s | `(a+b*x)^2/(x^2*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e842 | verified 0.1s | 3.8s | `(a+b*x)^2/(x^3*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e843 | verified 0.1s | 4.5s | `(a+b*x)^2/(x^4*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e844 | verified 0.1s | 3.7s | `x^3*(a+b*x)^2/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e845 | verified 0.1s | 3.7s | `x^2*(a+b*x)^2/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e846 | expected 0.1s | 3.9s | `x*(a+b*x)^2/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e847 | verified 0.1s | 4.0s | `(a+b*x)^2/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e848 | verified 0.1s | 3.8s | `(a+b*x)^2/(x*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e849 | verified 0.1s | 3.9s | `(a+b*x)^2/(x^2*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e850 | verified 0.1s | 4.0s | `(a+b*x)^2/(x^3*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e851 | verified 0.1s | 3.7s | `(a+b*x)^2/(x^4*(c*x^2)^(5/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e852 | verified 0.1s | 2.8s | `x^3*sqrt(c*x^2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e853 | verified 0.1s | 3.0s | `x^2*sqrt(c*x^2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e854 | verified 0.1s | 1.9s | `x*sqrt(c*x^2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e856 | expected 0.1s | 2.0s | `sqrt(c*x^2)/(x*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e858 | verified 0.1s | 3.8s | `sqrt(c*x^2)/(x^3*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e859 | verified 0.1s | 3.4s | `sqrt(c*x^2)/(x^4*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e860 | verified 0.1s | 3.2s | `x*(c*x^2)^(3/2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e861 | verified 0.1s | 3.4s | `(c*x^2)^(3/2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e862 | verified 0.2s | 2.1s | `(c*x^2)^(3/2)/(x*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e864 | expected 0.2s | 3.0s | `(c*x^2)^(3/2)/(x^3*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e866 | verified 0.1s | 5.2s | `(c*x^2)^(3/2)/(x^5*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e867 | verified 0.1s | 5.0s | `(c*x^2)^(3/2)/(x^6*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e868 | verified 0.1s | 5.6s | `(c*x^2)^(3/2)/(x^7*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e869 | verified 0.1s | 4.3s | `(c*x^2)^(5/2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e870 | verified 0.1s | 3.6s | `(c*x^2)^(5/2)/(x*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e871 | verified 0.1s | 3.8s | `(c*x^2)^(5/2)/(x^2*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e872 | verified 0.1s | 2.2s | `(c*x^2)^(5/2)/(x^3*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e874 | expected 0.1s | 2.8s | `(c*x^2)^(5/2)/(x^5*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e876 | verified 0.1s | 4.5s | `(c*x^2)^(5/2)/(x^7*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e877 | verified 0.1s | 2.1s | `x^4/((a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e878 | verified 0.1s | 1.3s | `x^3/((a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e880 | expected 0.1s | 2.1s | `x/((a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e882 | verified 0.1s | 3.2s | `1/(x*(a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e883 | verified 0.1s | 3.6s | `1/(x^2*(a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e884 | verified 0.1s | 4.0s | `1/(x^3*(a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e885 | verified 0.1s | 2.3s | `x^6/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e886 | verified 0.1s | 1.4s | `x^5/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e888 | expected 0.1s | 2.2s | `x^3/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e890 | verified 0.1s | 3.1s | `x/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e891 | verified 0.1s | 3.6s | `1/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e892 | verified 0.1s | 3.8s | `1/(x*(c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e893 | verified 0.1s | 3.3s | `x^3*sqrt(c*x^2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e894 | verified 0.1s | 3.4s | `x^2*sqrt(c*x^2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e895 | verified 0.1s | 2.2s | `x*sqrt(c*x^2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e896 | verified 0.1s | 1.0s | `sqrt(c*x^2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e897 | expected 0.1s | 2.6s | `sqrt(c*x^2)/(x*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e898 | verified 0.1s | 1.5s | `sqrt(c*x^2)/(x^2*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e899 | verified 0.1s | 3.6s | `sqrt(c*x^2)/(x^3*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e900 | verified 0.1s | 4.0s | `sqrt(c*x^2)/(x^4*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e901 | verified 0.1s | 3.2s | `x*(c*x^2)^(3/2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e902 | verified 0.1s | 2.9s | `(c*x^2)^(3/2)/(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e903 | verified 0.1s | 2.2s | `(c*x^2)^(3/2)/(x*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e904 | verified 0.1s | 1.0s | `(c*x^2)^(3/2)/(x^2*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e905 | expected 0.1s | 3.3s | `(c*x^2)^(3/2)/(x^3*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e906 | verified 0.1s | 1.5s | `(c*x^2)^(3/2)/(x^4*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e907 | verified 0.1s | 5.1s | `(c*x^2)^(3/2)/(x^5*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e908 | verified 0.1s | 5.4s | `(c*x^2)^(3/2)/(x^6*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e909 | verified 0.1s | 2.5s | `x^5/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e910 | verified 0.1s | 2.5s | `x^4/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e911 | verified 0.1s | 1.8s | `x^3/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e912 | verified 0.1s | 1.0s | `x^2/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e913 | expected 0.1s | 2.2s | `x/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e914 | verified 0.1s | 1.6s | `1/((a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e915 | verified 0.1s | 3.6s | `1/(x*(a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e916 | verified 0.1s | 3.6s | `1/(x^2*(a+b*x)^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e917 | verified 0.1s | 1.5s | `x^5/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e918 | verified 0.1s | 0.8s | `x^4/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e919 | expected 0.1s | 2.4s | `x^3/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e920 | verified 0.1s | 1.2s | `x^2/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e921 | verified 0.1s | 3.6s | `x/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e922 | verified 0.1s | 3.9s | `1/((c*x^2)^(3/2)*(a+b*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e923 | verified 0.2s | 1.9s | `x^2*(a+b*x)^n*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e924 | verified 0.1s | 1.2s | `x*(a+b*x)^n*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e925 | verified 0.2s | 0.6s | `(a+b*x)^n*sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e926 | expected 0.1s | 1.7s | `(a+b*x)^n*sqrt(c*x^2)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e927 | verified 0.2s | 1.5s | `(a+b*x)^n*sqrt(c*x^2)/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e928 | verified 0.1s | 2.1s | `(a+b*x)^n*sqrt(c*x^2)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e929 | verified 0.1s | 2.2s | `(a+b*x)^n*sqrt(c*x^2)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e930 | verified 0.2s | 1.8s | `x*(c*x^2)^(3/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e931 | verified 0.1s | 2.0s | `(c*x^2)^(3/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e932 | verified 0.2s | 1.2s | `(c*x^2)^(3/2)*(a+b*x)^n/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e933 | verified 0.1s | 0.6s | `(c*x^2)^(3/2)*(a+b*x)^n/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e934 | expected 0.1s | 2.8s | `(c*x^2)^(3/2)*(a+b*x)^n/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e935 | verified 0.1s | 2.3s | `(c*x^2)^(3/2)*(a+b*x)^n/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e936 | verified 0.1s | 2.9s | `(c*x^2)^(3/2)*(a+b*x)^n/x^5` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e937 | verified 0.1s | 2.9s | `(c*x^2)^(3/2)*(a+b*x)^n/x^6` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e938 | verified 0.1s | 1.8s | `(c*x^2)^(5/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e939 | verified 0.1s | 1.9s | `(c*x^2)^(5/2)*(a+b*x)^n/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e940 | verified 0.1s | 1.8s | `(c*x^2)^(5/2)*(a+b*x)^n/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e941 | verified 0.1s | 1.2s | `(c*x^2)^(5/2)*(a+b*x)^n/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e942 | verified 0.1s | 0.6s | `(c*x^2)^(5/2)*(a+b*x)^n/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e943 | expected 0.1s | 2.6s | `(c*x^2)^(5/2)*(a+b*x)^n/x^5` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e944 | verified 0.1s | 2.4s | `(c*x^2)^(5/2)*(a+b*x)^n/x^6` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e945 | verified 0.1s | 2.8s | `(c*x^2)^(5/2)*(a+b*x)^n/x^7` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e946 | verified 0.1s | 1.7s | `x^4*(a+b*x)^n/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e947 | verified 0.1s | 1.1s | `x^3*(a+b*x)^n/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e948 | verified 0.1s | 0.6s | `x^2*(a+b*x)^n/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e949 | expected 0.1s | 2.0s | `x*(a+b*x)^n/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e950 | verified 0.1s | 0.8s | `(a+b*x)^n/sqrt(c*x^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e951 | verified 0.1s | 2.8s | `(a+b*x)^n/(x*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e952 | verified 0.1s | 3.2s | `(a+b*x)^n/(x^2*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e953 | verified 0.1s | 1.8s | `x^6*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e954 | verified 0.1s | 1.2s | `x^5*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e955 | verified 0.1s | 0.6s | `x^4*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e956 | expected 0.1s | 1.9s | `x^3*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e957 | verified 0.1s | 0.9s | `x^2*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e958 | verified 0.1s | 2.9s | `x*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e959 | verified 0.1s | 2.8s | `(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e960 | verified 0.1s | 3.0s | `(a+b*x)^n/(x*(c*x^2)^(3/2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e961 | verified 0.1s | 1.8s | `x^8*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e962 | verified 0.1s | 1.5s | `x^7*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e963 | verified 0.1s | 0.6s | `x^6*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e964 | expected 0.1s | 2.0s | `x^5*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e965 | verified 0.1s | 0.8s | `x^4*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e966 | verified 0.1s | 3.0s | `x^3*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e967 | verified 0.1s | 3.0s | `x^2*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e968 | verified 0.1s | 3.1s | `x*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e969 | verified 0.1s | 1.9s | `(d*x)^m*(c*x^2)^(5/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e970 | verified 0.1s | 1.8s | `(d*x)^m*(c*x^2)^(3/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e971 | verified 0.1s | 1.8s | `(d*x)^m*(c*x^2)^(1/2)*(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e972 | verified 0.1s | 3.1s | `(d*x)^m*(a+b*x)/(c*x^2)^(1/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e973 | verified 0.1s | 3.5s | `(d*x)^m*(a+b*x)/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e974 | verified 0.1s | 3.7s | `(d*x)^m*(a+b*x)/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e975 | verified 0.1s | 3.0s | `(d*x)^m*(c*x^2)^(5/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e976 | verified 0.1s | 2.9s | `(d*x)^m*(c*x^2)^(3/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e977 | verified 0.1s | 2.7s | `(d*x)^m*(c*x^2)^(1/2)*(a+b*x)^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e978 | verified 0.1s | 5.6s | `(d*x)^m*(a+b*x)^2/(c*x^2)^(1/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e979 | verified 0.1s | 6.0s | `(d*x)^m*(a+b*x)^2/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e980 | verified 0.1s | 7.3s | `(d*x)^m*(a+b*x)^2/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e981 | verified 0.1s | 2.5s | `(d*x)^m*(c*x^2)^(5/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e982 | verified 0.1s | 2.5s | `(d*x)^m*(c*x^2)^(3/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e983 | verified 0.1s | 2.1s | `(d*x)^m*(c*x^2)^(1/2)*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e984 | verified 0.1s | 3.1s | `(d*x)^m*(a+b*x)^n/(c*x^2)^(1/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e985 | verified 0.1s | 3.5s | `(d*x)^m*(a+b*x)^n/(c*x^2)^(3/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e986 | verified 0.1s | 4.2s | `(d*x)^m*(a+b*x)^n/(c*x^2)^(5/2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e987 | expected 0.1s | 26.8s | `x^3*(c*x^2)^p*(a+b*x)^(-5-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e988 | expected 0.1s | 15.8s | `x^2*(c*x^2)^p*(a+b*x)^(-4-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e989 | expected 0.1s | 7.2s | `x*(c*x^2)^p*(a+b*x)^(-3-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e990 | expected 0.1s | 0.9s | `(c*x^2)^p*(a+b*x)^(-2-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e991 | expected 0.1s | 4.9s | `(c*x^2)^p*(a+b*x)^(-1-2*p)/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e992 | expected 0.2s | 3.2s | `(c*x^2)^p/(x^2*(a+b*x)^(2*p))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e993 | expected 0.1s | 5.7s | `(c*x^2)^p*(a+b*x)^(1-2*p)/x^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e994 | expected 0.1s | 6.3s | `(c*x^2)^p*(a+b*x)^(2-2*p)/x^4` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e995 | expected 0.1s | 3.6s | `x^m*(c*x^2)^p*(a+b*x)^(-2-m-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e996 | expected 0.3s | 3.8s | `(d*x)^m*(c*x^2)^p*(a+b*x)^(-2-m-2*p)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e997 | verified 0.2s | 3.1s | `x^m*(c*x^2)^p*(a+b*x)^n` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e998 | verified 0.2s | 3.3s | `(d*x)^m*(c*x^2)^p*(a+b*x)^n` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e65 | verified 0.0s | 0.5s | `(a+b*x)^2*(A+B*x)/x` |
| 1.1.1.4 (a+b x)^m (c+d x)^n (e+f x)^p (g+h x)^q | e143 | no-answer 0.1s | 12.6s | `(a+b*x)^m*(c+d*x)^n*(e+f*x)^p/(g+h*x)` |
| 1.1.2.2 (c x)^m (a+b x^2)^p | e19 | verified 0.0s | 0.6s | `(a+b*x^2)^2/x` |
| 1.1.2.2 (c x)^m (a+b x^2)^p | e20 | verified 0.0s | 3.4s | `(a+b*x^2)^2/x^2` |
| 1.1.2.2 (c x)^m (a+b x^2)^p | e21 | verified 0.0s | 0.6s | `(a+b*x^2)^2/x^3` |
| 1.1.2.2 (c x)^m (a+b x^2)^p | e22 | verified 0.0s | 3.5s | `(a+b*x^2)^2/x^4` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e4 | verified 0.0s | 1.2s | `(a+b*x^2)*(A+B*x^2)/x` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e6 | verified 0.0s | 1.0s | `(a+b*x^2)*(A+B*x^2)/x^3` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e14 | verified 0.0s | 0.6s | `(a+b*x^2)^2*(A+B*x^2)/x` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e146 | verified 0.0s | 0.5s | `(a+b*x^2)^2*(c+d*x^2)/x` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e671 | verified 0.1s | 2.6s | `x^5/((a+b*x^2)*sqrt(d*x^2))` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e672 | verified 0.1s | 1.3s | `x^3/((a+b*x^2)*sqrt(d*x^2))` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e673 | expected 0.1s | 1.9s | `x/((a+b*x^2)*sqrt(d*x^2))` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e674 | verified 0.1s | 3.6s | `1/(x*(a+b*x^2)*sqrt(d*x^2))` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e675 | verified 0.1s | 4.0s | `1/(x^3*(a+b*x^2)*sqrt(d*x^2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2 | expected 0.1s | 0.5s | `x^3*sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e3 | expected 0.1s | 0.5s | `x^2*sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e4 | expected 0.0s | 0.3s | `x*sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e5 | expected 0.0s | 0.2s | `sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e6 | expected 0.1s | 0.5s | `sqrt(b*x^2)/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e7 | expected 0.1s | 0.2s | `sqrt(b*x^2)/x^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e8 | expected 0.1s | 0.7s | `sqrt(b*x^2)/x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e9 | expected 0.1s | 0.8s | `sqrt(b*x^2)/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e10 | expected 0.1s | 0.7s | `sqrt(b*x^2)/x^5` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e12 | expected 0.1s | 0.5s | `x^2*(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e13 | expected 0.1s | 0.6s | `x*(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e14 | expected 0.1s | 0.5s | `(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e15 | expected 0.0s | 0.3s | `(b*x^2)^(3/2)/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e16 | expected 0.0s | 0.1s | `(b*x^2)^(3/2)/x^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e17 | expected 0.1s | 0.6s | `(b*x^2)^(3/2)/x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e18 | expected 0.1s | 0.2s | `(b*x^2)^(3/2)/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e19 | expected 0.1s | 1.2s | `(b*x^2)^(3/2)/x^5` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e20 | expected 0.1s | 1.1s | `(b*x^2)^(3/2)/x^6` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e21 | expected 0.1s | 1.0s | `(b*x^2)^(3/2)/x^7` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e23 | expected 0.1s | 0.5s | `x*(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e24 | expected 0.1s | 0.5s | `(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e25 | expected 0.1s | 0.5s | `(b*x^2)^(5/2)/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e26 | expected 0.1s | 0.5s | `(b*x^2)^(5/2)/x^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e27 | expected 0.0s | 0.3s | `(b*x^2)^(5/2)/x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e28 | expected 0.0s | 0.2s | `(b*x^2)^(5/2)/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e29 | expected 0.1s | 0.8s | `(b*x^2)^(5/2)/x^5` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e30 | expected 0.1s | 0.2s | `(b*x^2)^(5/2)/x^6` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e31 | expected 0.1s | 1.8s | `(b*x^2)^(5/2)/x^7` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e32 | expected 0.1s | 1.0s | `(b*x^2)^(5/2)/x^8` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e33 | expected 0.1s | 1.0s | `(b*x^2)^(5/2)/x^9` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e35 | expected 0.0s | 0.3s | `x^3/sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e36 | expected 0.1s | 0.5s | `x/sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e37 | expected 0.1s | 0.8s | `1/(x*sqrt(b*x^2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e38 | expected 0.1s | 0.8s | `1/(x^3*sqrt(b*x^2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e39 | expected 0.0s | 0.1s | `x^2/sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e40 | expected 0.1s | 0.2s | `1/sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e41 | expected 0.1s | 0.8s | `1/(x^2*sqrt(b*x^2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e42 | expected 0.0s | 0.3s | `x^5/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e43 | expected 0.1s | 0.5s | `x^3/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e44 | expected 0.1s | 0.8s | `x/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e45 | expected 0.1s | 0.7s | `1/(x*(b*x^2)^(3/2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e46 | expected 0.1s | 0.8s | `1/(x^3*(b*x^2)^(3/2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e47 | expected 0.1s | 0.5s | `x^6/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e48 | expected 0.0s | 0.2s | `x^4/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e49 | expected 0.1s | 0.3s | `x^2/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e50 | expected 0.1s | 0.8s | `1/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e51 | expected 0.1s | 0.8s | `1/(x^2*(b*x^2)^(3/2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e52 | expected 0.0s | 0.3s | `x^7/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e53 | expected 0.1s | 0.5s | `x^5/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e54 | expected 0.1s | 0.8s | `x^3/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e55 | expected 0.1s | 0.8s | `x/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e56 | expected 0.1s | 0.8s | `1/(x*(b*x^2)^(5/2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e57 | expected 0.0s | 0.2s | `x^6/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e58 | expected 0.1s | 0.2s | `x^4/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e59 | expected 0.1s | 0.8s | `x^2/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e60 | expected 0.1s | 0.8s | `1/(b*x^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e61 | expected 0.1s | 0.8s | `1/(x^2*(b*x^2)^(5/2))` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e62 | expected 0.1s | 0.9s | `(c*x)^m*(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e63 | expected 0.1s | 0.5s | `(c*x)^m*(b*x^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e64 | expected 0.1s | 0.8s | `(c*x)^m/(b*x^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e65 | expected 0.1s | 1.5s | `(c*x)^m/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e66 | expected 0.1s | 1.0s | `x^m*(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e67 | expected 0.1s | 0.8s | `(c*x)^m*(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e69 | expected 0.1s | 0.8s | `x^3*(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e70 | expected 0.1s | 0.8s | `x^2*(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e71 | expected 0.1s | 0.6s | `x*(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e72 | expected 0.1s | 0.3s | `(b*x^2)^p` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e73 | expected 0.1s | 0.8s | `(b*x^2)^p/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e74 | expected 0.1s | 0.7s | `(b*x^2)^p/x^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e75 | expected 0.1s | 0.8s | `(b*x^2)^p/x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e76 | expected 0.1s | 0.8s | `(b*x^2)^p/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e78 | expected 0.0s | 0.2s | `sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e81 | expected 0.1s | 0.2s | `sqrt(b/x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e84 | expected 0.1s | 0.5s | `(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e87 | expected 0.1s | 1.0s | `(b/x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e90 | expected 0.1s | 0.2s | `1/sqrt(b*x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e93 | expected 0.0s | 0.1s | `1/sqrt(b/x^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e96 | expected 0.1s | 0.7s | `1/(b*x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e99 | expected 0.1s | 0.5s | `1/(b/x^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e223 | verified 0.0s | 0.5s | `(a+b*x^3)^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e225 | verified 0.0s | 3.5s | `(a+b*x^3)^2/x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e226 | verified 0.0s | 0.5s | `(a+b*x^3)^2/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e228 | verified 0.0s | 3.5s | `(a+b*x^3)^2/x^6` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e625 | verified 0.1s | 0.6s | `(a+b*x^4)^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e628 | verified 0.1s | 3.7s | `(a+b*x^4)^2/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e629 | verified 0.1s | 0.5s | `(a+b*x^4)^2/x^5` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1438 | verified 0.1s | 0.5s | `(a+b*x^7)^2/x^8` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1818 | verified 0.0s | 0.5s | `(a+b/x^2)^2*x^3` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1819 | verified 0.1s | 3.4s | `(a+b/x^2)^2*x^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1820 | verified 0.1s | 0.5s | `(a+b/x^2)^2*x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1821 | verified 0.1s | 3.4s | `(a+b/x^2)^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2123 | verified 0.1s | 0.5s | `(a+b*sqrt(x))^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2292 | verified 0.1s | 0.4s | `(a+b*x^(1/3))^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2455 | verified 0.1s | 0.5s | `(a+b*x^n)^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2525 | verified 0.1s | 0.5s | `(a+b*x^n)^2/x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2526 | verified 0.1s | 0.5s | `x^(-1-n)*(a+b*x^n)^2` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2795 | expected 0.2s | 0.8s | `(c*(a+b*x)^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2796 | expected 0.2s | 0.8s | `(c*(a+b*x)^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2797 | expected 0.1s | 0.2s | `(c*(a+b*x)^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2798 | expected 0.1s | 0.3s | `1/(c*(a+b*x)^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2799 | expected 0.1s | 1.3s | `1/(c*(a+b*x)^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2800 | expected 0.1s | 1.4s | `1/(c*(a+b*x)^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2801 | expected 0.1s | 0.1s | `sqrt((3+5*x)^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2802 | expected 0.1s | 0.1s | `sqrt((6+10*x)^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2805 | expected 0.1s | 0.2s | `1/sqrt(-(2+3*x)^2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2818 | expected 0.1s | 3.2s | `(c/(a+b*x)^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2819 | expected 0.1s | 2.3s | `(c/(a+b*x)^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2820 | expected 0.1s | 0.4s | `(c/(a+b*x)^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2821 | expected 0.1s | 0.2s | `1/(c/(a+b*x)^2)^(1/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2822 | expected 0.1s | 1.2s | `1/(c/(a+b*x)^2)^(3/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2823 | expected 0.1s | 1.6s | `1/(c/(a+b*x)^2)^(5/2)` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e2831 | verified 0.1s | 0.2s | `(c*(a+b*x)^(2/3))^(3/2)` |
| 1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q | e4 | verified 0.0s | 1.3s | `(a+b*x^3)*(A+B*x^3)/x` |
| 1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q | e7 | verified 0.0s | 1.0s | `(a+b*x^3)*(A+B*x^3)/x^4` |
| 1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q | e14 | verified 0.0s | 0.6s | `(a+b*x^3)^2*(A+B*x^3)/x` |
| 1.1.4.2 (c x)^m (a x^j+b x^n)^p | e344 | verified 0.0s | 3.5s | `(a/x+b*x)^2` |
| 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | e6 | verified 0.1s | 1.6s | `(A+B*x^2)*(b*x^2+c*x^4)/x^3` |
| 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | e8 | verified 0.1s | 1.2s | `(A+B*x^2)*(b*x^2+c*x^4)/x^5` |
| 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | e17 | verified 0.1s | 1.0s | `(A+B*x^2)*(b*x^2+c*x^4)^2/x^5` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e123 | verified 0.1s | 1.6s | `x*(A+B*x)/(b*x+c*x^2)^(3/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e150 | verified 0.1s | 15.9s | `x^3/((1+a*x)*sqrt(1-a^2*x^2))` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e472 | verified 0.1s | 2.2s | `x/((d+e*x)*sqrt(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e50 | verified 0.1s | 28.5s | `(d+e*x)^3*(A+B*x+C*x^2)/(a+c*x^2)^2` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e65 | verified 0.1s | 29.6s | `(d+e*x)^3*(A+B*x+C*x^2)/(a+c*x^2)^4` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e150 | verified 0.2s | 0.7s | `(b*x^2+c*x^4)^2/x^5` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e151 | verified 0.2s | 3.3s | `(b*x^2+c*x^4)^2/x^6` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e152 | verified 0.1s | 0.8s | `(b*x^2+c*x^4)^2/x^7` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e153 | verified 0.2s | 3.3s | `(b*x^2+c*x^4)^2/x^8` |
| 1.3.1 Rational functions | e250 | verified 0.1s | 11.7s | `x^3*(5+x+3*x^2+2*x^3)/(2+x+5*x^2+x^3+2*x^4)` |
| 1.3.1 Rational functions | e251 | verified 0.1s | 12.6s | `x^2*(5+x+3*x^2+2*x^3)/(2+x+5*x^2+x^3+2*x^4)` |
| 1.3.1 Rational functions | e252 | verified 0.1s | 8.8s | `x*(5+x+3*x^2+2*x^3)/(2+x+5*x^2+x^3+2*x^4)` |
| 1.3.2 Algebraic functions | e209 | verified 0.1s | 2.4s | `sqrt(a*x^6)/(x*(1-x^4))` |
| 1.3.2 Algebraic functions | e210 | verified 0.1s | 2.9s | `sqrt(a*x^6)/(x-x^5)` |
| 1.3.2 Algebraic functions | e211 | verified 0.1s | 3.6s | `(a*x^6)^(3/2)/(x*(1-x^4))` |
| 1.3.2 Algebraic functions | e212 | verified 0.1s | 1.2s | `1/(1-x^4)-sqrt(a*x^6)/(x*(1-x^4))` |
| 1.3.2 Algebraic functions | e213 | verified 0.5s | 1.2s | `1/(1-x^4)-sqrt(a*x^6)/(x-x^5)` |
| 1.3.2 Algebraic functions | e217 | expected 0.2s | 0.6s | `sqrt(a*x^2)/sqrt(1+x^2)` |
| 1.3.2 Algebraic functions | e220 | expected 0.1s | 0.8s | `sqrt(a/x^2)/sqrt(1+x^2)` |
| 1.3.2 Algebraic functions | e225 | verified 0.1s | 0.6s | `sqrt(a*x^2)/sqrt(1+x^3)` |
| 1.3.2 Algebraic functions | e228 | expected 0.1s | 0.9s | `sqrt(a/x^2)/sqrt(1+x^3)` |
| 1.3.2 Algebraic functions | e649 | verified 0.1s | 0.7s | `(-1+x+x^2)/(1+sqrt(1+x^2))` |
| 1.3.2 Algebraic functions | e650 | expected 0.2s | 5.2s | `(-1+x+x^2)/(1+x+sqrt(1+x^2))` |
| 1.3.2 Algebraic functions | e660 | verified 0.1s | 2.5s | `(x-sqrt(x^6))/(x*(1-x^4))` |
| 1.3.2 Algebraic functions | e661 | verified 0.1s | 1.7s | `(1-sqrt(x^6)/x)/(1-x^4)` |
| 1.3.2 Algebraic functions | e662 | verified 0.1s | 2.6s | `(x-sqrt(x^6))/(x-x^5)` |
| 1.3.2 Algebraic functions | e673 | verified 0.1s | 0.5s | `sqrt(1+2*x^2)/(1+sqrt(1+2*x^2))` |
| 1.3.2 Algebraic functions | e724 | verified 0.1s | 1.8s | `x*sqrt(2-x^2)/(x-sqrt(2-x^2))` |
| 1.3.2 Algebraic functions | e758 | no-answer 0.1s | 1.3s | `F(x)*sqrt(x-x^2)` |
| 1.3.2 Algebraic functions | e759 | no-answer 0.1s | 0.8s | `F(x)/sqrt(x-x^2)` |
| 1.3.2 Algebraic functions | e760 | no-answer 0.1s | 1.2s | `F(x)*sqrt(1-x)*sqrt(x)` |
| 1.3.2 Algebraic functions | e761 | no-answer 0.1s | 0.7s | `F(x)/(sqrt(1-x)*sqrt(x))` |
| 1.3.2 Algebraic functions | e796 | verified 0.1s | 0.4s | `(-1+x)/(1+sqrt(1+x^2))` |

### rubi timeout (263)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 1.1.1.2 (a+b x)^m (c+d x)^n | e370 | expected 0.0s | 30.1s | `x^(1/2*(1-n)+1/2*(-3+n))/sqrt(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1007 | expected 0.1s | 30.0s | `(b*c/d+b*x)^5/(c+d*x)^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1259 | verified 0.2s | 30.1s | `(a+b*x)^4*(c+d*x)^3` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1274 | verified 0.1s | 30.1s | `(a+b*x)^8*(c+d*x)^7` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1276 | verified 0.1s | 30.1s | `(a+b*x)^6*(c+d*x)^7` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1278 | verified 0.1s | 30.1s | `(a+b*x)^4*(c+d*x)^7` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1300 | verified 0.5s | 30.1s | `(a+b*x)^11*(c+d*x)^10` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1302 | verified 0.3s | 30.1s | `(a+b*x)^9*(c+d*x)^10` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1304 | verified 0.1s | 30.1s | `(a+b*x)^7*(c+d*x)^10` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1308 | verified 0.3s | 30.1s | `(a+b*x)^3*(c+d*x)^10` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1351 | verified 0.1s | 30.1s | `1/((a+b*x)^3*(c+d*x)^2)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1360 | verified 0.1s | 30.1s | `1/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1361 | verified 0.1s | 30.1s | `1/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1372 | verified 0.2s | 30.1s | `1/((a+b*x)*(c+d*x)^8)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1373 | verified 0.3s | 30.1s | `1/((a+b*x)^2*(c+d*x)^8)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1374 | verified 0.4s | 30.1s | `1/((a+b*x)^3*(c+d*x)^8)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e259 | verified 0.1s | 30.0s | `x^7/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e260 | verified 0.1s | 30.1s | `x^6/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e261 | verified 0.1s | 30.1s | `x^5/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e262 | verified 0.1s | 30.0s | `x^4/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e263 | verified 0.1s | 30.1s | `x^3/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e264 | verified 0.1s | 30.1s | `x^2/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e265 | verified 0.1s | 30.1s | `x/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e266 | verified 0.1s | 30.1s | `1/((a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e267 | verified 0.1s | 30.1s | `1/(x*(a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e268 | verified 0.1s | 30.0s | `1/(x^2*(a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e269 | verified 0.1s | 30.0s | `1/(x^3*(a+b*x)^2*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e279 | verified 0.1s | 30.1s | `x^7/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e280 | verified 0.1s | 30.1s | `x^6/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e281 | verified 0.1s | 30.1s | `x^5/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e282 | verified 0.1s | 30.1s | `x^4/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e283 | verified 0.1s | 30.0s | `x^3/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e284 | verified 0.1s | 30.0s | `x^2/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e285 | verified 0.1s | 30.1s | `x/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e286 | verified 0.1s | 30.0s | `1/((a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e287 | verified 0.1s | 30.0s | `1/(x*(a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e288 | verified 0.1s | 30.0s | `1/(x^2*(a+b*x)^3*(c+d*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1040 | verified 0.1s | 30.0s | `(a+b*x)^6*(A+B*x)*(d+e*x)^7` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1065 | verified 0.1s | 30.1s | `(a+b*x)^10*(A+B*x)*(d+e*x)^11` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1109 | verified 0.1s | 30.1s | `(A+B*x)/((a+b*x)*(d+e*x)^5)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1118 | verified 0.1s | 30.0s | `(A+B*x)/((a+b*x)^2*(d+e*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1119 | verified 0.1s | 30.1s | `(A+B*x)/((a+b*x)^2*(d+e*x)^4)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1120 | verified 0.1s | 30.1s | `(A+B*x)/((a+b*x)^2*(d+e*x)^5)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1128 | verified 0.1s | 30.1s | `(A+B*x)/((a+b*x)^3*(d+e*x)^2)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1129 | verified 0.1s | 30.0s | `(A+B*x)/((a+b*x)^3*(d+e*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1130 | verified 0.1s | 30.1s | `(A+B*x)/((a+b*x)^3*(d+e*x)^4)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1703 | verified 0.2s | 30.0s | `1/((a+b*x)^2*(c+d*x)^2*(e+f*x)^2)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1704 | verified 10.0s | 30.1s | `1/((a+b*x)^3*(c+d*x)^3*(e+f*x)^3)` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1769 | verified 0.1s | 30.1s | `(a+b*x)^2/((c+d*x)*(e+f*x)^(9/2))` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1777 | verified 0.1s | 30.0s | `(a+b*x)^3/((c+d*x)*(e+f*x)^(9/2))` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1951 | verified 0.1s | 30.1s | `(1-2*x)^(5/2)*(3+5*x)^3/(2+3*x)^4` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1952 | verified 0.1s | 30.0s | `(1-2*x)^(5/2)*(3+5*x)^3/(2+3*x)^5` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e1953 | verified 0.1s | 30.1s | `(1-2*x)^(5/2)*(3+5*x)^3/(2+3*x)^6` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e6 | verified 0.1s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^2*sqrt(c+d*x))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e7 | verified 0.2s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^3*sqrt(c+d*x))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e8 | verified 0.4s | 30.0s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^4*sqrt(c+d*x))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e9 | verified 0.8s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^5*sqrt(c+d*x))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e15 | verified 0.2s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^2*(c+d*x)^(3/2))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e16 | verified 0.4s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^3*(c+d*x)^(3/2))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e17 | verified 1.0s | 30.0s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^4*(c+d*x)^(3/2))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e23 | verified 0.2s | 30.1s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^2*(c+d*x)^(5/2))` |
| 1.1.1.5 P(x) (a+b x)^m (c+d x)^n | e24 | verified 0.5s | 30.0s | `(A+B*x+C*x^2+D*x^3)/((a+b*x)^3*(c+d*x)^(5/2))` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e311 | verified 0.1s | 30.1s | `x^3/((a+b*x^2)^2*(c+d*x^2)^3)` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e313 | verified 0.1s | 30.0s | `x/((a+b*x^2)^2*(c+d*x^2)^3)` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e315 | verified 0.1s | 30.0s | `1/(x*(a+b*x^2)^2*(c+d*x^2)^3)` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e317 | verified 0.1s | 30.0s | `1/(x^3*(a+b*x^2)^2*(c+d*x^2)^3)` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e439 | verified 12.3s | 30.1s | `(a+b*x^2)^2/(x^(5/2)*(c+d*x^2)^3)` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e440 | verified 13.1s | 30.1s | `(a+b*x^2)^2/(x^(7/2)*(c+d*x^2)^3)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e6 | verified 0.1s | 30.1s | `(c+d*x+e*x^2+f*x^3)^3/sqrt(a+b*x)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e261 | verified 0.1s | 30.1s | `x^7*(c+d*x^3+e*x^6+f*x^9)/(a+b*x^3)^2` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e275 | verified 0.1s | 30.1s | `(c+d*x^3+e*x^6+f*x^9)/(x^14*(a+b*x^3)^2)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e286 | verified 0.1s | 30.0s | `x^12*(c+d*x^3+e*x^6+f*x^9)/(a+b*x^3)^3` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e287 | verified 0.2s | 30.1s | `x^10*(c+d*x^3+e*x^6+f*x^9)/(a+b*x^3)^3` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e288 | verified 0.2s | 30.1s | `x^9*(c+d*x^3+e*x^6+f*x^9)/(a+b*x^3)^3` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e289 | verified 0.2s | 30.1s | `x^7*(c+d*x^3+e*x^6+f*x^9)/(a+b*x^3)^3` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e301 | verified 0.1s | 30.0s | `(c+d*x^3+e*x^6+f*x^9)/(x^11*(a+b*x^3)^3)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e302 | verified 0.1s | 30.1s | `(c+d*x^3+e*x^6+f*x^9)/(x^12*(a+b*x^3)^3)` |
| 1.1.3.8 P(x) (c x)^m (a+b x^n)^p | e303 | verified 0.1s | 30.1s | `(c+d*x^3+e*x^6+f*x^9)/(x^14*(a+b*x^3)^3)` |
| 1.1.4.2 (c x)^m (a x^j+b x^n)^p | e330 | expected 0.0s | 30.0s | `x^24*(a*x+b*x^38)^12` |
| 1.1.4.2 (c x)^m (a x^j+b x^n)^p | e351 | expected 0.1s | 30.0s | `x^12*(a*x^2+b*x^39)^12` |
| 1.1.4.2 (c x)^m (a x^j+b x^n)^p | e353 | expected 0.1s | 30.1s | `x^24*(a*x+b*x^38)^12` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e284 | verified 0.1s | 30.1s | `1/((d+e*x)^2*(b*x+c*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e473 | verified 0.1s | 30.0s | `(d+e*x)^5*(a+c*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e474 | verified 0.1s | 30.1s | `(d+e*x)^4*(a+c*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e488 | verified 0.1s | 30.1s | `(d+e*x)^7*(a+c*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e490 | verified 0.1s | 30.1s | `(d+e*x)^5*(a+c*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e495 | verified 0.1s | 30.1s | `(a+c*x^2)^4/(d+e*x)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e836 | verified 0.1s | 30.1s | `(d+e*x)^6/(d^2-e^2*x^2)^(5/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e846 | verified 0.1s | 30.1s | `(d+e*x)^9/(d^2-e^2*x^2)^(7/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e847 | verified 0.1s | 30.1s | `(d+e*x)^8/(d^2-e^2*x^2)^(7/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1017 | expected 0.1s | 30.1s | `(d+e*x)^9/(c*d^2+2*c*d*e*x+c*e^2*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1155 | verified 0.1s | 30.1s | `(b*d+2*c*d*x)^7/(a+b*x+c*x^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1167 | verified 0.1s | 30.1s | `(b*d+2*c*d*x)^7/(a+b*x+c*x^2)^2` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1178 | verified 0.1s | 30.0s | `(b*d+2*c*d*x)^9/(a+b*x+c*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1180 | verified 0.2s | 30.1s | `(b*d+2*c*d*x)^7/(a+b*x+c*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1464 | verified 0.1s | 30.1s | `(d+e*x)^5*(a^2+2*a*b*x+b^2*x^2)^2` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1466 | verified 0.1s | 30.1s | `(d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^2` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1482 | verified 0.1s | 30.1s | `(d+e*x)^7*(a^2+2*a*b*x+b^2*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1484 | verified 0.1s | 30.1s | `(d+e*x)^5*(a^2+2*a*b*x+b^2*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1490 | verified 0.1s | 30.1s | `(a^2+2*a*b*x+b^2*x^2)^3/(d+e*x)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1513 | verified 0.2s | 30.1s | `1/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2))` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1514 | verified 0.3s | 30.1s | `1/((d+e*x)^4*(a^2+2*a*b*x+b^2*x^2))` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1523 | verified 0.1s | 30.1s | `1/((d+e*x)^2*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1524 | verified 0.2s | 30.1s | `1/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1534 | verified 0.1s | 30.0s | `1/((d+e*x)*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1535 | verified 0.2s | 30.1s | `1/((d+e*x)^2*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1536 | verified 0.2s | 30.1s | `1/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1555 | verified 0.2s | 30.0s | `(d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^(3/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1570 | verified 0.1s | 30.1s | `(d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^(5/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1785 | verified 0.0s | 30.0s | `(a+b*x)*(a*c+(b*c+a*d)*x+b*d*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1809 | verified 0.1s | 30.0s | `1/((a+b*x)^4*(a*c+(b*c+a*d)*x+b*d*x^2))` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1817 | verified 0.0s | 30.1s | `1/((a+b*x)*(a*c+(b*c+a*d)*x+b*d*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1825 | verified 0.0s | 30.1s | `(a+b*x)/(a*c+(b*c+a*d)*x+b*d*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1827 | verified 0.1s | 30.0s | `1/((a+b*x)*(a*c+(b*c+a*d)*x+b*d*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1852 | verified 0.1s | 30.1s | `(d+e*x)*(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1854 | verified 0.1s | 30.1s | `(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3/(d+e*x)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1883 | verified 0.1s | 30.0s | `1/((d+e*x)*(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1884 | verified 0.1s | 30.1s | `1/((d+e*x)^2*(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1885 | verified 0.1s | 30.0s | `(d+e*x)^9/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1893 | verified 0.0s | 30.1s | `(d+e*x)/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1895 | verified 0.1s | 30.1s | `1/((d+e*x)*(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1897 | verified 0.0s | 30.1s | `(d+e*x)^9/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1904 | verified 0.1s | 30.1s | `(d+e*x)^2/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1905 | verified 0.1s | 30.1s | `(d+e*x)/(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2131 | verified 0.0s | 30.1s | `(d+e*x)^4*(a+b*x+c*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2147 | verified 0.1s | 30.1s | `(d+e*x)^3*(a+b*x+c*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2151 | verified 0.0s | 30.1s | `(a+b*x+c*x^2)^4/(d+e*x)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2189 | verified 0.1s | 30.0s | `1/((d+e*x)^3*(a+b*x+c*x^2))` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2197 | verified 1.7s | 30.0s | `1/((d+e*x)^2*(a+b*x+c*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2198 | verified 1.8s | 30.1s | `1/((d+e*x)^3*(a+b*x+c*x^2)^2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2207 | verified 0.1s | 30.0s | `1/((d+e*x)*(a+b*x+c*x^2)^3)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2210 | verified 0.1s | 30.0s | `x^8/(a+b*x+c*x^2)^4` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2219 | verified 0.5s | 30.1s | `1/((d+e*x)*(a+b*x+c*x^2)^4)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2227 | verified 1.5s | 30.1s | `1/((d+e*x)*(a+b*x+c*x^2)^5)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2228 | verified 8.6s | 30.1s | `1/((d+e*x)^2*(a+b*x+c*x^2)^5)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e28 | verified 0.1s | 30.0s | `x^3*(A+B*x)*(b*x+c*x^2)^3` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e120 | verified 0.9s | 30.0s | `x^4*(A+B*x)/(b*x+c*x^2)^(3/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e121 | verified 0.6s | 30.1s | `x^3*(A+B*x)/(b*x+c*x^2)^(3/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e868 | verified 0.1s | 30.1s | `x*(A+B*x)*(a+b*x+c*x^2)^3` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1153 | verified 0.1s | 30.0s | `(A+B*x)/((d+e*x)^3*(b*x+c*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1161 | verified 0.1s | 30.0s | `(A+B*x)/((d+e*x)^2*(b*x+c*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1530 | verified 0.2s | 30.1s | `(b+2*c*x)/((d+e*x)^2*(a+b*x+c*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1531 | verified 0.2s | 30.1s | `(b+2*c*x)/((d+e*x)^3*(a+b*x+c*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1537 | verified 0.1s | 30.0s | `(b+2*c*x)/((d+e*x)*(a+b*x+c*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1538 | verified 0.1s | 30.0s | `(b+2*c*x)/((d+e*x)^2*(a+b*x+c*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1545 | verified 0.2s | 30.1s | `(b+2*c*x)/((d+e*x)*(a+b*x+c*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1700 | verified 0.1s | 30.0s | `(A+B*x)/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1707 | verified 0.1s | 30.1s | `(A+B*x)/((d+e*x)^2*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1896 | verified 0.0s | 30.1s | `(a+b*x)*(d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1905 | verified 0.0s | 30.0s | `(a+b*x)*(d+e*x)^6*(a^2+2*a*b*x+b^2*x^2)^2` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1907 | verified 0.0s | 30.1s | `(a+b*x)*(d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^2` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1916 | verified 0.1s | 30.1s | `(a+b*x)*(d+e*x)^6*(a^2+2*a*b*x+b^2*x^2)^3` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1918 | verified 0.1s | 30.0s | `(a+b*x)*(d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^3` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1942 | verified 0.0s | 30.0s | `(a+b*x)/((d+e*x)^2*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1943 | verified 0.1s | 30.1s | `(a+b*x)/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1944 | verified 0.1s | 30.1s | `(a+b*x)/((d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1950 | verified 0.1s | 30.1s | `(a+b*x)/((d+e*x)*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1951 | verified 0.1s | 30.0s | `(a+b*x)/((d+e*x)^2*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1952 | verified 0.1s | 30.1s | `(a+b*x)/((d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1953 | verified 0.1s | 30.1s | `(a+b*x)/((d+e*x)^4*(a^2+2*a*b*x+b^2*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1968 | verified 0.1s | 30.1s | `(a+b*x)*(d+e*x)^7*(a^2+2*a*b*x+b^2*x^2)^(3/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1970 | verified 0.1s | 30.1s | `(a+b*x)*(d+e*x)^5*(a^2+2*a*b*x+b^2*x^2)^(3/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1972 | verified 0.0s | 30.0s | `(a+b*x)*(d+e*x)^3*(a^2+2*a*b*x+b^2*x^2)^(3/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1988 | verified 0.2s | 30.1s | `(a+b*x)*(d+e*x)^9*(a^2+2*a*b*x+b^2*x^2)^(5/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1990 | verified 0.1s | 30.0s | `(a+b*x)*(d+e*x)^7*(a^2+2*a*b*x+b^2*x^2)^(5/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e1992 | verified 0.1s | 30.1s | `(a+b*x)*(d+e*x)^5*(a^2+2*a*b*x+b^2*x^2)^(5/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2179 | verified 0.2s | 30.1s | `(f+g*x)*sqrt(c*d^2-b*d*e-b*e^2*x-c*e^2*x^2)/(d+e*x)^5` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2180 | verified 0.4s | 30.0s | `(f+g*x)*sqrt(c*d^2-b*d*e-b*e^2*x-c*e^2*x^2)/(d+e*x)^6` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2181 | verified 0.5s | 30.1s | `(f+g*x)*sqrt(c*d^2-b*d*e-b*e^2*x-c*e^2*x^2)/(d+e*x)^7` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2182 | verified 0.9s | 30.1s | `(f+g*x)*sqrt(c*d^2-b*d*e-b*e^2*x-c*e^2*x^2)/(d+e*x)^8` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2318 | verified 0.0s | 30.0s | `(A+B*x)*(d+e*x)^5*(a+b*x+c*x^2)^2` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2369 | verified 0.0s | 30.1s | `(A+B*x)/((d+e*x)^2*(a+b*x+c*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2370 | verified 0.1s | 30.1s | `(A+B*x)/((d+e*x)^3*(a+b*x+c*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2376 | verified 0.2s | 30.1s | `(f+g*x)/((d+e*x)*(a+b*x+c*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2377 | verified 1.0s | 30.0s | `(f+g*x)/((d+e*x)^2*(a+b*x+c*x^2)^3)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2415 | verified 0.1s | 30.1s | `(5-x)*sqrt(2+5*x+3*x^2)/(3+2*x)^5` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2416 | verified 0.1s | 30.1s | `(5-x)*sqrt(2+5*x+3*x^2)/(3+2*x)^6` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2417 | verified 0.1s | 30.1s | `(5-x)*sqrt(2+5*x+3*x^2)/(3+2*x)^7` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2429 | verified 0.3s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(3/2)/(3+2*x)^7` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2430 | verified 0.5s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(3/2)/(3+2*x)^8` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2431 | verified 0.7s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(3/2)/(3+2*x)^9` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2445 | verified 1.8s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(5/2)/(3+2*x)^9` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2446 | verified 2.3s | 30.0s | `(5-x)*(2+5*x+3*x^2)^(5/2)/(3+2*x)^10` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2462 | verified 3.9s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(7/2)/(3+2*x)^11` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2463 | verified 3.3s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(7/2)/(3+2*x)^12` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2464 | verified 12.1s | 30.1s | `(5-x)*(2+5*x+3*x^2)^(7/2)/(3+2*x)^13` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2480 | verified 0.2s | 30.0s | `(A+B*x)*(d+e*x)^4/(a+b*x+c*x^2)^(5/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2487 | verified 1.2s | 30.0s | `(A+B*x)*(d+e*x)^6/(a+b*x+c*x^2)^(7/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2488 | verified 1.1s | 30.1s | `(A+B*x)*(d+e*x)^5/(a+b*x+c*x^2)^(7/2)` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2503 | verified 0.1s | 30.1s | `(5-x)/((3+2*x)^4*sqrt(2+5*x+3*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2504 | verified 0.1s | 30.1s | `(5-x)/((3+2*x)^5*sqrt(2+5*x+3*x^2))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e2505 | verified 0.4s | 30.1s | `(5-x)/((3+2*x)^6*sqrt(2+5*x+3*x^2))` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e20 | verified 0.1s | 30.0s | `x^6*(d+e*x)/(d^2-e^2*x^2)^(7/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e817 | verified 0.1s | 30.1s | `1/((d+e*x)*(f+g*x)*(a+b*x+c*x^2))` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e818 | verified 0.3s | 30.1s | `1/((d+e*x)*(f+g*x)*(a+b*x+c*x^2)^2)` |
| 1.2.1.5 (a+b x+c x^2)^p (d+e x+f x^2)^q | e118 | verified 0.4s | 30.0s | `(d+e*x+f*x^2)^3/(a+b*x+c*x^2)^(5/2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e8 | verified 0.1s | 30.1s | `(A+B*x+C*x^2)*sqrt(d^2-e^2*x^2)/(d+e*x)^5` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e9 | verified 0.2s | 30.1s | `(A+B*x+C*x^2)*sqrt(d^2-e^2*x^2)/(d+e*x)^6` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e16 | verified 0.1s | 30.1s | `(A+B*x+C*x^2)/((d+e*x)^3*sqrt(d^2-e^2*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e17 | verified 0.2s | 30.1s | `(A+B*x+C*x^2)/((d+e*x)^4*sqrt(d^2-e^2*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e56 | verified 0.2s | 30.0s | `(A+B*x+C*x^2)/((d+e*x)^3*(a+c*x^2)^2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e62 | verified 0.2s | 30.1s | `(A+B*x+C*x^2)/((d+e*x)^2*(a+c*x^2)^3)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e63 | verified 0.2s | 30.1s | `(A+B*x+C*x^2)/((d+e*x)^3*(a+c*x^2)^3)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e64 | verified 0.1s | 30.0s | `(d+e*x)^4*(A+B*x+C*x^2)/(a+c*x^2)^4` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e146 | verified 0.1s | 30.1s | `(A+C*x^2)/(a+b*x+c*x^2)^3` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e153 | verified 0.1s | 30.0s | `(f+g*x+h*x^2)/((d+e*x)^2*(a+b*x+c*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e154 | verified 0.1s | 30.1s | `(f+g*x+h*x^2)/((d+e*x)^3*(a+b*x+c*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e158 | verified 0.1s | 30.0s | `(f+g*x+h*x^2)/((d+e*x)*(a+b*x+c*x^2)^2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e159 | verified 0.2s | 30.0s | `(f+g*x+h*x^2)/((d+e*x)^2*(a+b*x+c*x^2)^2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e258 | verified 0.3s | 30.1s | `(d+e*x+f*x^2)/((g+h*x)*(-c*g^2+b*g*h+b*h^2*x+c*h^2*x^2)^(3/2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e278 | expected 0.2s | 30.1s | `(d+e*x)^3*(a+b*x+c*x^2)^5*(d*(6*b*d+5*a*e)+(12*c*d^2+17*b*d*e+5*a*e^2)*x+e*(29*c*d+11*b*e)*x^2+17*c*e^2*x^3)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e309 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)^2*(3+2*x+5*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e310 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)^3*(3+2*x+5*x^2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e316 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)^2*(3+2*x+5*x^2)^2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e317 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)^3*(3+2*x+5*x^2)^2)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e322 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)*(3+2*x+5*x^2)^3)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e323 | verified 0.1s | 30.1s | `(2+x+3*x^2-5*x^3+4*x^4)/((d+e*x)^2*(3+2*x+5*x^2)^3)` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e333 | verified 0.1s | 30.0s | `(2+x+3*x^2-x^3+5*x^4)*sqrt(3-x+2*x^2)/(5+2*x)^8` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e343 | verified 0.1s | 30.0s | `(3-x+2*x^2)^(3/2)*(2+x+3*x^2-x^3+5*x^4)/(5+2*x)^8` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e364 | verified 0.1s | 30.1s | `(2+x+3*x^2-x^3+5*x^4)/((5+2*x)^4*(3-x+2*x^2)^(5/2))` |
| 1.2.1.9 P(x) (d+e x)^m (a+b x+c x^2)^p | e372 | verified 0.1s | 30.0s | `(d+e*x+f*x^2+g*x^3+h*x^4+i*x^5)/(a+b*x+c*x^2)^3` |
| 1.2.2.3 (d+e x^2)^m (a+b x^2+c x^4)^p | e275 | verified 0.2s | 30.1s | `1/((d+e*x^2)^2*(a+b*x^2+c*x^4)^2)` |
| 1.2.2.4 (f x)^m (d+e x^2)^q (a+b x^2+c x^4)^p | e95 | verified 0.1s | 30.1s | `x^3*(A+B*x^2)*(a+b*x^2+c*x^4)^3` |
| 1.2.2.5 P(x) (a+b x^2+c x^4)^p | e40 | verified 0.1s | 30.1s | `(d+e*x+f*x^2+g*x^3+h*x^4+i*x^5)/(a+b*x^2+c*x^4)^2` |
| 1.2.2.5 P(x) (a+b x^2+c x^4)^p | e56 | verified 0.1s | 30.1s | `(d+e*x+f*x^2+g*x^3+h*x^4+i*x^5)/(a+b*x^2+c*x^4)^3` |
| 1.2.2.5 P(x) (a+b x^2+c x^4)^p | e57 | verified 0.2s | 30.0s | `(d+e*x+f*x^2+g*x^3+h*x^4+j*x^5+k*x^6+l*x^7+m*x^8)/(a+b*x^2+c*x^4)^3` |
| 1.2.2.5 P(x) (a+b x^2+c x^4)^p | e59 | verified 0.2s | 30.1s | `(d+e*x+f*x^2+g*x^3+h*x^4+i*x^5+j*x^8+k*x^11)/(a+b*x^2+c*x^4)^3` |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e68 | verified 0.1s | 30.1s | `x^6*(d+e*x^2+f*x^4)/(a+b*x^2+c*x^4)^2` |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e126 | verified 0.1s | 30.1s | `x^4*(d+e*x^2+f*x^4+g*x^6)/(a+b*x^2+c*x^4)^2` |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e129 | verified 0.1s | 30.0s | `(d+e*x^2+f*x^4+g*x^6)/(x^2*(a+b*x^2+c*x^4)^2)` |
| 1.2.2.6 P(x) (d x)^m (a+b x^2+c x^4)^p | e130 | verified 0.1s | 30.0s | `(d+e*x^2+f*x^4+g*x^6)/(x^4*(a+b*x^2+c*x^4)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e70 | verified 0.1s | 30.1s | `x^3/((a+c/x^2+b/x)*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e71 | verified 0.2s | 30.0s | `x^2/((a+c/x^2+b/x)*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e72 | verified 0.2s | 30.1s | `x/((a+c/x^2+b/x)*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e73 | verified 0.1s | 30.1s | `1/((a+c/x^2+b/x)*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e74 | verified 0.1s | 30.0s | `1/((a+c/x^2+b/x)*x*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e76 | verified 0.2s | 30.1s | `1/((a+c/x^2+b/x)*x^3*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e77 | verified 0.3s | 30.1s | `1/((a+c/x^2+b/x)*x^4*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e78 | verified 0.1s | 30.0s | `1/((a+c/x^2+b/x)*x^5*(d+e*x)^2)` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e94 | expected 0.1s | 30.1s | `x*(b+2*c*x^2)*(a+b*x^2+c*x^4)^13` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e98 | expected 0.1s | 30.1s | `x*(b+2*c*x^2)*(-a+b*x^2+c*x^4)^13` |
| 1.2.3.4 (f x)^m (d+e x^n)^q (a+b x^n+c x^(2 n))^p | e102 | expected 0.1s | 30.1s | `x*(b+2*c*x^2)*(b*x^2+c*x^4)^13` |
| 1.3.1 Rational functions | e19 | verified 0.3s | 30.1s | `1/(a*c*e+(b*c*e+a*d*e+a*c*f)*x+(b*d*e+b*c*f+a*d*f)*x^2+b*d*f*x^3)^2` |
| 1.3.1 Rational functions | e20 | verified 16.1s | 30.0s | `1/(a*c*e+(b*c*e+a*d*e+a*c*f)*x+(b*d*e+b*c*f+a*d*f)*x^2+b*d*f*x^3)^3` |
| 1.3.1 Rational functions | e33 | verified 0.1s | 30.0s | `(4*a*c+4*c^2*x^2+4*c*d*x^3+d^2*x^4)^4` |
| 1.3.1 Rational functions | e39 | verified 0.1s | 30.0s | `(8*a*e^2-d^3*x+8*d*e^2*x^3+8*e^3*x^4)^4` |
| 1.3.1 Rational functions | e58 | verified 0.1s | 30.1s | `(8+24*x+8*x^2-15*x^3+8*x^4)^3` |
| 1.3.1 Rational functions | e107 | verified 0.1s | 30.1s | `1/(x*(a+b*(c+d*x)^3))` |
| 1.3.1 Rational functions | e115 | verified 0.2s | 30.0s | `1/(x^2*(a+b*(c+d*x)^4))` |
| 1.3.1 Rational functions | e161 | expected 0.1s | 30.1s | `x^14*(b+2*c*x^2)*(b*x+c*x^3)^13` |
| 1.3.1 Rational functions | e192 | expected 0.1s | 30.1s | `(b+2*c*x+3*d*x^2)*(a+b*x+c*x^2+d*x^3)^7` |
| 1.3.1 Rational functions | e198 | expected 0.1s | 30.0s | `(2*c*x+3*d*x^2)*(a+c*x^2+d*x^3)^7` |
| 1.3.1 Rational functions | e199 | expected 0.1s | 30.2s | `(2*c*x+3*d*x^2)*(c*x^2+d*x^3)^7` |
| 1.3.1 Rational functions | e200 | expected 0.1s | 30.1s | `x^7*(c*x+d*x^2)^7*(2*c*x+3*d*x^2)` |
| 1.3.1 Rational functions | e201 | expected 0.1s | 30.2s | `x^14*(c+d*x)^7*(2*c*x+3*d*x^2)` |
| 1.3.1 Rational functions | e210 | verified 0.1s | 30.1s | `(a+c*x^2)*(1+(a*x+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e211 | verified 0.1s | 30.1s | `(a+c*x^2)*(1+(d+a*x+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e212 | verified 0.1s | 30.1s | `(b*x+c*x^2)*(1+(1/2*b*x^2+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e213 | verified 0.1s | 30.0s | `(b*x+c*x^2)*(1+(d+1/2*b*x^2+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e214 | verified 0.1s | 30.0s | `(a+b*x+c*x^2)*(1+(a*x+1/2*b*x^2+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e215 | verified 0.5s | 30.0s | `(a+b*x+c*x^2)*(1+(d+a*x+1/2*b*x^2+1/3*c*x^3)^5)` |
| 1.3.1 Rational functions | e493 | expected 0.0s | 30.0s | `3*(-47+228*x+120*x^2+19*x^3)/(3+x+x^4)^4+(42-320*x-75*x^2-8*x^3)/(3+x+x^4)^3+30*x/(3+x+x^4)^2` |
| 1.3.1 Rational functions | e494 | expected 0.0s | 30.1s | `(-3+10*x+4*x^3-30*x^5)/(3+x+x^4)^3-3*(1+4*x^3)*(2-3*x+5*x^2+x^4-5*x^6)/(3+x+x^4)^4` |

### rubi deferred (27)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 1.1.1.2 (a+b x)^m (c+d x)^n | e56 | verified 0.0s | 0.5s | `(a+b*x)^2/x` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e57 | verified 0.0s | 0.5s | `(a+b*x)^2/x^2` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e855 | verified 0.3s | 0.5s | `sqrt(c*x^2)/(a+b*x)` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e857 | verified 0.1s | 0.7s | `sqrt(c*x^2)/(x^2*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e863 | verified 0.2s | 0.5s | `(c*x^2)^(3/2)/(x^2*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e865 | verified 0.2s | 0.8s | `(c*x^2)^(3/2)/(x^4*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e873 | verified 0.1s | 0.6s | `(c*x^2)^(5/2)/(x^4*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e875 | verified 0.1s | 0.9s | `(c*x^2)^(5/2)/(x^6*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e879 | verified 0.1s | 0.4s | `x^2/((a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e881 | verified 0.1s | 0.5s | `1/((a+b*x)*sqrt(c*x^2))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e887 | verified 0.1s | 0.4s | `x^4/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e889 | verified 0.1s | 0.6s | `x^2/((c*x^2)^(3/2)*(a+b*x))` |
| 1.1.1.2 (a+b x)^m (c+d x)^n | e1907 | verified 0.1s | 0.3s | `1+1/x+x` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e54 | verified 0.0s | 1.3s | `(a+b*x)*(A+B*x)/x` |
| 1.1.1.3 (a+b x)^m (c+d x)^n (e+f x)^p | e55 | verified 0.0s | 1.0s | `(a+b*x)*(A+B*x)/x^2` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e5 | verified 0.0s | 0.6s | `(a+b*x^2)*(A+B*x^2)/x^2` |
| 1.1.2.4 (e x)^m (a+b x^2)^p (c+d x^2)^q | e7 | verified 0.0s | 0.5s | `(a+b*x^2)*(A+B*x^2)/x^4` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1561 | verified 0.1s | 0.5s | `(a+b/x)^2*x` |
| 1.1.3.2 (c x)^m (a+b x^n)^p | e1562 | verified 0.1s | 0.5s | `(a+b/x)^2` |
| 1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q | e6 | verified 0.0s | 0.5s | `(a+b*x^3)*(A+B*x^3)/x^3` |
| 1.1.3.4 (e x)^m (a+b x^n)^p (c+d x^n)^q | e9 | verified 0.0s | 0.5s | `(a+b*x^3)*(A+B*x^3)/x^6` |
| 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | e7 | verified 0.1s | 1.0s | `(A+B*x^2)*(b*x^2+c*x^4)/x^4` |
| 1.1.4.3 (e x)^m (a x^j+b x^k)^p (c+d x^n)^q | e9 | verified 0.1s | 0.8s | `(A+B*x^2)*(b*x^2+c*x^4)/x^6` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e7 | verified 0.1s | 1.2s | `(A+B*x)*(b*x+c*x^2)/x^2` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e8 | verified 0.1s | 1.0s | `(A+B*x)*(b*x+c*x^2)/x^3` |
| 1.3.1 Rational functions | e50 | verified 0.1s | 0.4s | `1/(8+8*x-x^3+8*x^4)^2` |
| 1.3.1 Rational functions | e62 | verified 0.3s | 0.4s | `1/(8+24*x+8*x^2-15*x^3+8*x^4)^2` |

### rubi unverified (27)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 1.2.1.1 (a+b x+c x^2)^p | e98 | verified 0.1s | 0.2s | `1/((a/b)^(2/n)+x^2-2*(a/b)^(1/n)*x*cos((%pi-2*%pi*k)/n))` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e824 | verified 0.1s | 0.6s | `sqrt(1-x^2)/(1-x)^2` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e837 | verified 0.1s | 0.2s | `(d+e*x)^5/(d^2-e^2*x^2)^(5/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e848 | verified 0.1s | 0.2s | `(d+e*x)^7/(d^2-e^2*x^2)^(7/2)` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1786 | verified 0.0s | 3.8s | `(a*c+(b*c+a*d)*x+b*d*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e1853 | verified 0.0s | 4.2s | `(a*d*e+(c*d^2+a*e^2)*x+c*d*e*x^2)^3` |
| 1.2.1.2 (d+e x)^m (a+b x+c x^2)^p | e2235 | verified 0.0s | 0.9s | `2*((a/b)^(1/n)-x*cos(%pi*(-1+2*k)/n))/((a/b)^(2/n)+x^2-2*(a/b)^(1/n)*x*cos(%pi*(-1+2*k)/n))` |
| 1.2.1.3 (d+e x)^m (f+g x) (a+b x+c x^2)^p | e122 | verified 0.3s | 0.9s | `x^2*(A+B*x)/(b*x+c*x^2)^(3/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e17 | verified 0.1s | 0.2s | `x^2*(d+e*x)/(d^2-e^2*x^2)^(3/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e32 | verified 0.1s | 0.2s | `x^2*(1-a*x)/(1-a^2*x^2)^(3/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e85 | verified 0.1s | 2.1s | `x^3*(d+e*x)^3/(d^2-e^2*x^2)^(7/2)` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e151 | verified 0.1s | 0.2s | `x^2/((1+a*x)*sqrt(1-a^2*x^2))` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e152 | verified 0.1s | 0.9s | `x/((1+a*x)*sqrt(1-a^2*x^2))` |
| 1.2.1.4 (d+e x)^m (f+g x)^n (a+b x+c x^2)^p | e581 | verified 0.2s | 4.0s | `(d+e*x)^3*(f+g*x)^3/(d^2-e^2*x^2)^(7/2)` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1021 | expected 0.0s | 0.1s | `x^4/sqrt(2+2*a-2*(1+a)+c*x^4)` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1023 | expected 0.1s | 0.9s | `x^2/sqrt(2+2*a-2*(1+a)+c*x^4)` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1025 | expected 0.0s | 0.1s | `1/sqrt(2+2*a-2*(1+a)+c*x^4)` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1026 | expected 0.0s | 0.1s | `1/(x*sqrt(2+2*a-2*(1+a)+c*x^4))` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1027 | expected 0.0s | 0.8s | `1/(x^2*sqrt(2+2*a-2*(1+a)+c*x^4))` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1029 | expected 0.0s | 0.1s | `1/(x^4*sqrt(2+2*a-2*(1+a)+c*x^4))` |
| 1.2.2.2 (d x)^m (a+b x^2+c x^4)^p | e1030 | expected 0.1s | 0.1s | `x^4/sqrt(a+(2+2*c-2*(1+c))*x^4)` |
| 1.3.1 Rational functions | e483 | verified 0.0s | 0.1s | `(x+1/2*(3-sqrt(37)))*(x+1/2*(3+sqrt(37)))` |
| 1.3.2 Algebraic functions | e215 | verified 0.1s | 0.8s | `sqrt(a*x^4)/sqrt(1+x^2)` |
| 1.3.2 Algebraic functions | e222 | expected 0.1s | 0.6s | `sqrt(a/x^4)/sqrt(1+x^2)` |
| 1.3.2 Algebraic functions | e230 | verified 0.1s | 0.6s | `sqrt(a/x^4)/sqrt(1+x^3)` |
| 1.3.2 Algebraic functions | e708 | verified 0.0s | 1.1s | `(1+x)^3/(x*(1-x^2)^(3/2))` |
| 1.3.2 Algebraic functions | e710 | verified 0.0s | 1.3s | `(1+a*x)^3/(x*(1-a^2*x^2)^(3/2))` |

### rubi error (3)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 1.3.1 Rational functions | e193 | expected 0.1s | 8.3s | `(b+2*c*x+3*d*x^2)*(b*x+c*x^2+d*x^3)^7` |
| 1.3.1 Rational functions | e194 | expected 0.1s | 8.9s | `x^7*(b+c*x+d*x^2)^7*(b+2*c*x+3*d*x^2)` |
| 1.3.1 Rational functions | e195 | expected 0.1s | 3.0s | `(b+3*d*x^2)*(a+b*x+d*x^3)^7` |

## Class 2 (22)

### rubi contains-noun (10)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 2.3 Exponential functions | e28 | verified 0.0s | 0.7s | `(a+%e^(n*x)*b)^2/%e^(n*x)` |
| 2.3 Exponential functions | e65 | expected 0.0s | 1.0s | `f^(a+b*x+c*x^2)*g^(d+e*x+f*x^2)` |
| 2.3 Exponential functions | e466 | verified 0.1s | 0.9s | `%e^(a+b*x)*x^2/(c+d*x^2)` |
| 2.3 Exponential functions | e471 | verified 0.1s | 2.7s | `%e^(d+e*x)*x^2/(a+b*x+c*x^2)` |
| 2.3 Exponential functions | e472 | verified 0.2s | 3.2s | `%e^(d+e*x)*x^3/(a+b*x+c*x^2)` |
| 2.3 Exponential functions | e750 | expected 0.1s | 2.9s | `1/5*x^2*(5*%e^x+3*x^2)/sqrt(5*%e^x+x^3)+4/5*x*sqrt(5*%e^x+x^3)` |
| 2.3 Exponential functions | e755 | expected 0.1s | 2.0s | `(5*x+%e^x*(3+2*x))/(%e^x+x)^(1/3)` |
| 2.3 Exponential functions | e756 | expected 0.1s | 1.0s | `2*x/(%e^x+x)^(1/3)+2*%e^x*x/(%e^x+x)^(1/3)+3*(%e^x+x)^(2/3)` |
| 2.3 Exponential functions | e758 | no-answer 0.1s | 0.5s | `x/(%e^x+x)` |
| 2.3 Exponential functions | e774 | verified 0.1s | 3.4s | `(5*x^2+3*(%e^x+x)^(1/3)+%e^x*(3*x+2*x^2))/(x*(%e^x+x)^(1/3))` |

### rubi deferred (10)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 2.3 Exponential functions | e438 | verified 0.2s | 0.6s | `%e^((a+b*x)*(c+d*x))*x^3` |
| 2.3 Exponential functions | e439 | verified 0.2s | 0.6s | `%e^((a+b*x)*(c+d*x))*x^2` |
| 2.3 Exponential functions | e440 | verified 0.2s | 0.4s | `%e^((a+b*x)*(c+d*x))*x` |
| 2.3 Exponential functions | e441 | expected 0.1s | 0.2s | `%e^((a+b*x)*(c+d*x))` |
| 2.3 Exponential functions | e465 | verified 0.1s | 0.8s | `%e^(a+b*x)*x/(c+d*x^2)` |
| 2.3 Exponential functions | e470 | verified 0.1s | 0.9s | `%e^(d+e*x)*x/(a+b*x+c*x^2)` |
| 2.3 Exponential functions | e510 | verified 0.1s | 0.3s | `x/(1+2*%e^x+%e^(2*x))` |
| 2.3 Exponential functions | e515 | verified 0.1s | 0.4s | `x^2/(1+2*%e^x+%e^(2*x))` |
| 2.3 Exponential functions | e530 | verified 0.2s | 0.9s | `x/(2+1/%e^x+%e^x)` |
| 2.3 Exponential functions | e531 | verified 0.1s | 1.2s | `x^2/(2+1/%e^x+%e^x)` |

### rubi timeout (2)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 2.1 u (F^(c (a+b x)))^n | e74 | verified 0.1s | 30.0s | `%e^(-a-b*x)*(a+b*x)^4*(c+d*x)^3` |
| 2.3 Exponential functions | e620 | verified 0.2s | 30.1s | `%e^(a+b*x+c*x^2)*(b+2*c*x)*(a+b*x+c*x^2)^3` |

## Class 3 (66)

### rubi timeout (46)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e404 | verified 0.1s | 30.1s | `(d+e*x^r)^3*(a+b*log(c*x^n))/x^8` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e405 | verified 0.1s | 30.1s | `(d+e*x^r)^3*(a+b*log(c*x^n))/x^10` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e8 | verified 0.1s | 30.0s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(a*g+b*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e9 | verified 0.1s | 30.1s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(a*g+b*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e36 | verified 0.1s | 30.1s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(c*g+d*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e37 | verified 0.1s | 30.1s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(c*g+d*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e65 | verified 0.1s | 30.1s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(f+g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e66 | verified 0.2s | 30.0s | `(A+B*log(e*((a+b*x)/(c+d*x))^n))/(f+g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e95 | verified 0.1s | 30.0s | `(A+B*log(e*(a+b*x)/(c+d*x)))/(a*g+b*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e96 | verified 0.1s | 30.1s | `(A+B*log(e*(a+b*x)/(c+d*x)))/(a*g+b*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e126 | verified 0.1s | 30.1s | `(A+B*log(e*(a+b*x)^2/(c+d*x)^2))/(a*g+b*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e127 | verified 0.1s | 30.0s | `(A+B*log(e*(a+b*x)^2/(c+d*x)^2))/(a*g+b*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e155 | verified 0.1s | 30.1s | `(A+B*log(e*(a+b*x)^n/(c+d*x)^n))/(a+b*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e180 | verified 0.1s | 30.0s | `(A+B*log(e*(c+d*x)/(a+b*x)))/(a*g+b*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e181 | verified 0.1s | 30.1s | `(A+B*log(e*(c+d*x)/(a+b*x)))/(a*g+b*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e208 | verified 0.1s | 30.0s | `(A+B*log(e*(c+d*x)^2/(a+b*x)^2))/(a*g+b*g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e209 | verified 0.1s | 30.0s | `(A+B*log(e*(c+d*x)^2/(a+b*x)^2))/(a*g+b*g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e238 | verified 0.1s | 30.1s | `(A+B*log(e*(a+b*x)/(c+d*x)))/(f+g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e239 | verified 0.2s | 30.1s | `(A+B*log(e*(a+b*x)/(c+d*x)))/(f+g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e270 | verified 0.1s | 30.0s | `(A+B*log(e*(a+b*x)^2/(c+d*x)^2))/(f+g*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e271 | verified 0.2s | 30.1s | `(A+B*log(e*(a+b*x)^2/(c+d*x)^2))/(f+g*x)^5` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e301 | verified 0.2s | 30.1s | `(A+B*log(e*(a+b*x)^n/(c+d*x)^n))/(g+h*x)^4` |
| 3.2.1 (f+g x)^m (A+B log(e ((a+b x) over (c+d x))^n))^p | e302 | verified 0.3s | 30.1s | `(A+B*log(e*(a+b*x)^n/(c+d*x)^n))/(g+h*x)^5` |
| 3.2.2 (f+g x)^m (h+i x)^q (A+B log(e ((a+b x) over (c+d x))^n))^p | e10 | verified 0.1s | 30.1s | `(a*g+b*g*x)^3*(c*i+d*i*x)^2*(A+B*log(e*(a+b*x)/(c+d*x)))` |
| 3.2.2 (f+g x)^m (h+i x)^q (A+B log(e ((a+b x) over (c+d x))^n))^p | e21 | verified 0.1s | 30.0s | `(a*g+b*g*x)^2*(c*i+d*i*x)^3*(A+B*log(e*(a+b*x)/(c+d*x)))` |
| 3.2.2 (f+g x)^m (h+i x)^q (A+B log(e ((a+b x) over (c+d x))^n))^p | e117 | verified 0.1s | 30.1s | `(a*g+b*g*x)^3*(c*i+d*i*x)^2*(A+B*log(e*((a+b*x)/(c+d*x))^n))` |
| 3.2.2 (f+g x)^m (h+i x)^q (A+B log(e ((a+b x) over (c+d x))^n))^p | e128 | verified 0.1s | 30.1s | `(a*g+b*g*x)^2*(c*i+d*i*x)^3*(A+B*log(e*((a+b*x)/(c+d*x))^n))` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e23 | verified 0.2s | 30.0s | `log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2/(a+b*x)^4` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e24 | verified 0.2s | 30.1s | `log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2/(a+b*x)^5` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e34 | verified 0.2s | 30.1s | `log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)/(g+h*x)^5` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e35 | verified 0.1s | 30.1s | `(g+h*x)^3*log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e42 | verified 4.1s | 30.1s | `log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2/(g+h*x)^4` |
| 3.3 u (a+b log(c (d+e x)^n))^p | e52 | verified 0.1s | 30.1s | `(f+g*x)^3*(a+b*log(c*(d+e*x)^n))^3` |
| 3.3 u (a+b log(c (d+e x)^n))^p | e428 | verified 0.1s | 30.0s | `(g+h*x)^3*(a+b*log(c*(d*(e+f*x)^p)^q))^2` |
| 3.3 u (a+b log(c (d+e x)^n))^p | e435 | verified 0.1s | 30.1s | `(g+h*x)^2*(a+b*log(c*(d*(e+f*x)^p)^q))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e415 | verified 0.1s | 30.1s | `x^2*(a+b*log(c*(d+e*sqrt(x))^n))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e441 | verified 0.1s | 30.0s | `(a+b*log(c*(d+e/sqrt(x))^n))^3/x^4` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e456 | verified 0.1s | 30.1s | `x^3*(a+b*log(c*(d+e*x^(1/3))^n))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e457 | verified 0.1s | 30.0s | `x^2*(a+b*log(c*(d+e*x^(1/3))^n))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e458 | verified 0.1s | 30.1s | `x*(a+b*log(c*(d+e*x^(1/3))^n))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e481 | verified 0.0s | 30.1s | `x^3*(a+b*log(c*(d+e*x^(2/3))^n))^3` |
| 3.4 u (a+b log(c (d+e x^m)^n))^p | e507 | verified 0.1s | 30.0s | `(a+b*log(c*(d+e/x^(1/3))^n))^3/x^3` |
| 3.5 Logarithm functions | e83 | verified 0.1s | 30.0s | `(d+e*x)^3*log(d*(a+b*x+c*x^2)^n)` |
| 3.5 Logarithm functions | e89 | verified 0.1s | 30.0s | `log(d*(a+b*x+c*x^2)^n)/(d+e*x)^3` |
| 3.5 Logarithm functions | e90 | verified 0.1s | 30.1s | `log(d*(a+b*x+c*x^2)^n)/(d+e*x)^4` |
| 3.5 Logarithm functions | e91 | verified 0.1s | 30.1s | `log(d*(a+b*x+c*x^2)^n)/(d+e*x)^5` |

### rubi contains-noun (19)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e13 | verified 0.1s | 1.2s | `(d+e*x)^2*(a+b*log(c*x^n))/x` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e14 | verified 0.1s | 1.6s | `(d+e*x)^2*(a+b*log(c*x^n))/x^2` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e66 | verified 0.1s | 7.5s | `x^4*(a+b*log(c*x^n))/(d+e*x)^7` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e186 | verified 0.1s | 1.6s | `(d+e*x^2)^2*(a+b*log(c*x^n))/x` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e187 | verified 0.1s | 1.6s | `(d+e*x^2)^2*(a+b*log(c*x^n))/x^3` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e192 | verified 0.1s | 4.7s | `(d+e*x^2)^2*(a+b*log(c*x^n))/x^2` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e193 | verified 0.1s | 4.7s | `(d+e*x^2)^2*(a+b*log(c*x^n))/x^4` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e382 | verified 0.1s | 1.7s | `(d+e*x^r)^2*(a+b*log(c*x^n))/x` |
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e422 | verified 0.2s | 1.7s | `(d+e*x^r)^2*(a+b*log(c*x^n))/x` |
| 3.2.3 u log(e (f (a+b x)^p (c+d x)^q)^r)^s | e37 | verified 0.1s | 15.9s | `(g+h*x)*log(e*(f*(a+b*x)^p*(c+d*x)^q)^r)^2` |
| 3.3 u (a+b log(c (d+e x)^n))^p | e346 | no-answer 0.1s | 1.5s | `1/((d*x+e*x^2)*log(c*(a+b*x)^n))` |
| 3.3 u (a+b log(c (d+e x)^n))^p | e374 | verified 0.1s | 1.3s | `log(x)*log(a+b*x)^2/x` |
| 3.5 Logarithm functions | e99 | verified 0.1s | 6.7s | `log(1+x+x^2)^2` |
| 3.5 Logarithm functions | e100 | verified 0.1s | 10.3s | `log(-1+x+x^2)^2/x^3` |
| 3.5 Logarithm functions | e286 | no-answer 0.1s | 0.5s | `x^2/(x+log(x))` |
| 3.5 Logarithm functions | e287 | no-answer 0.1s | 0.4s | `x/(x+log(x))` |
| 3.5 Logarithm functions | e289 | no-answer 0.1s | 0.5s | `1/(x*(x+log(x)))` |
| 3.5 Logarithm functions | e290 | no-answer 0.1s | 0.8s | `1/(x^2*(x+log(x)))` |
| 3.5 Logarithm functions | e293 | verified 0.1s | 1.2s | `(1+x)/(log(x)*(x+log(x)))` |

### rubi unexpected (1)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 3.1.4 (f x)^m (d+e x^r)^q (a+b log(c x^n))^p | e168 | no-answer 0.1s | 4.0s | `x*(a+b*x)^m*log(c*x^n)` |

## Class 4 (158)

### rubi contains-noun (91)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 4.1.1.3 (g tan)^p (a+b sin)^m | e208 | no-answer 0.2s | 2.8s | `(a+b*sin(e+f*x))^m*(g*tan(e+f*x))^p` |
| 4.1.10 (c+d x)^m (a+b sin)^n | e71 | no-answer 0.1s | 0.7s | `(c+d*x)^m*(b*sin(e+f*x))^n` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e158 | no-answer 0.1s | 0.6s | `sin(b*(c+d*x)^2)/(e+f*x)^2` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e170 | no-answer 0.2s | 0.6s | `sin(a+b*(c+d*x)^2)/(e+f*x)^2` |
| 4.1.2.2 (g cos)^p (a+b sin)^m (c+d sin)^n | e1560 | no-answer 0.9s | 2.4s | `(g*cos(e+f*x))^(-1-m)*(a+b*sin(e+f*x))^m*(A+B*sin(e+f*x))` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e3 | verified 0.1s | 0.6s | `(a*sin(x)^2)^(1/2)` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e4 | verified 0.1s | 0.3s | `1/(a*sin(x)^2)^(1/2)` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e5 | verified 0.1s | 3.3s | `1/(a*sin(x)^2)^(3/2)` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e6 | verified 0.1s | 3.6s | `1/(a*sin(x)^2)^(5/2)` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e26 | verified 0.1s | 1.5s | `(c*sin(a+b*x)^2)^p` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e28 | verified 0.1s | 1.6s | `(c*sin(a+b*x)^4)^p` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e434 | no-answer 0.3s | 1.4s | `sec(e+f*x)*(a+b*sin(e+f*x)^n)^p` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e435 | no-answer 0.3s | 2.9s | `sec(e+f*x)^3*(a+b*sin(e+f*x)^n)^p` |
| 4.2.0 (a cos)^m (b trg)^n | e39 | verified 0.3s | 3.4s | `(a*cos(x)^2)^(5/2)` |
| 4.2.0 (a cos)^m (b trg)^n | e40 | verified 0.2s | 2.5s | `(a*cos(x)^2)^(3/2)` |
| 4.2.0 (a cos)^m (b trg)^n | e41 | verified 0.2s | 0.4s | `(a*cos(x)^2)^(1/2)` |
| 4.2.0 (a cos)^m (b trg)^n | e42 | verified 0.1s | 0.3s | `1/(a*cos(x)^2)^(1/2)` |
| 4.2.0 (a cos)^m (b trg)^n | e43 | verified 0.1s | 3.5s | `1/(a*cos(x)^2)^(3/2)` |
| 4.2.0 (a cos)^m (b trg)^n | e44 | verified 0.1s | 6.5s | `1/(a*cos(x)^2)^(5/2)` |
| 4.2.10 (c+d x)^m (a+b cos)^n | e98 | no-answer 0.1s | 0.8s | `(c+d*x)^m*(b*cos(e+f*x))^n` |
| 4.2.12 (e x)^m (a+b cos(c+d x^n))^p | e89 | no-answer 0.1s | 0.5s | `cos((a+b*x)^2)/x^2` |
| 4.2.3.1 (a+b cos)^m (c+d cos)^n (A+B cos) | e449 | no-answer 0.4s | 2.3s | `(c*cos(e+f*x))^m*(a+b*cos(e+f*x))^n*(A+B*cos(e+f*x))` |
| 4.2.3.1 (a+b cos)^m (c+d cos)^n (A+B cos) | e456 | no-answer 0.4s | 2.3s | `(c*cos(e+f*x))^m*(a+b*cos(e+f*x))^(1/2)*(A+B*cos(e+f*x))` |
| 4.2.3.1 (a+b cos)^m (c+d cos)^n (A+B cos) | e457 | no-answer 0.4s | 2.3s | `(c*cos(e+f*x))^m*(A+B*cos(e+f*x))/(a+b*cos(e+f*x))^(1/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e24 | verified 0.2s | 1.3s | `(b*tan(c+d*x)^2)^(5/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e25 | verified 0.2s | 1.2s | `(b*tan(c+d*x)^2)^(3/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e26 | verified 0.1s | 0.3s | `(b*tan(c+d*x)^2)^(1/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e27 | verified 0.1s | 0.5s | `1/(b*tan(c+d*x)^2)^(1/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e28 | verified 0.2s | 1.8s | `1/(b*tan(c+d*x)^2)^(3/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e29 | verified 0.3s | 2.2s | `1/(b*tan(c+d*x)^2)^(5/2)` |
| 4.3.0 (a trg)^m (b tan)^n | e43 | verified 0.1s | 0.5s | `(b*tan(c+d*x)^2)^n` |
| 4.3.0 (a trg)^m (b tan)^n | e45 | verified 0.1s | 0.5s | `(b*tan(c+d*x)^4)^n` |
| 4.3.1.3 (d sin)^m (a+b tan)^n | e90 | no-answer 0.2s | 7.5s | `csc(c+d*x)*(a+b*tan(c+d*x))^n` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e1 | verified 0.2s | 1.3s | `(b*tan(e+f*x)^2)^(5/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e2 | verified 0.2s | 1.2s | `(b*tan(e+f*x)^2)^(3/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e3 | verified 0.1s | 0.3s | `(b*tan(e+f*x)^2)^(1/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e4 | verified 0.1s | 0.5s | `1/(b*tan(e+f*x)^2)^(1/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e5 | verified 0.2s | 1.9s | `1/(b*tan(e+f*x)^2)^(3/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e6 | verified 0.3s | 2.0s | `1/(b*tan(e+f*x)^2)^(5/2)` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e26 | verified 0.1s | 0.5s | `(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e28 | verified 0.1s | 0.5s | `(b*tan(e+f*x)^4)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e152 | verified 0.1s | 16.6s | `(d*sin(e+f*x))^m*(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e174 | no-answer 0.5s | 0.8s | `(d*sin(e+f*x))^m*(a+b*tan(e+f*x)^n)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e175 | verified 0.1s | 14.2s | `(d*cos(e+f*x))^m*(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e359 | verified 0.1s | 2.1s | `(d*tan(e+f*x))^m*(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e420 | no-answer 0.9s | 0.8s | `(d*tan(e+f*x))^m*(a+b*(c*tan(e+f*x))^n)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e421 | verified 0.2s | 2.3s | `(d*cot(e+f*x))^m*(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e474 | verified 0.1s | 14.8s | `(d*sec(e+f*x))^m*(b*tan(e+f*x)^2)^p` |
| 4.3.7 (d trig)^m (a+b (c tan)^n)^p | e486 | no-answer 0.4s | 0.9s | `(d*sec(e+f*x))^m*(a+b*(c*tan(e+f*x))^n)^p` |
| 4.4.0 (a trg)^m (b cot)^n | e25 | verified 0.2s | 1.5s | `(a*cot(x)^2)^(3/2)` |
| 4.4.0 (a trg)^m (b cot)^n | e26 | verified 0.1s | 0.2s | `sqrt(a*cot(x)^2)` |
| 4.4.0 (a trg)^m (b cot)^n | e27 | verified 0.1s | 0.5s | `1/sqrt(a*cot(x)^2)` |
| 4.4.0 (a trg)^m (b cot)^n | e28 | verified 0.2s | 1.3s | `1/(a*cot(x)^2)^(3/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e47 | verified 0.1s | 16.0s | `(a*sec(x)^2)^(7/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e48 | verified 0.1s | 7.1s | `(a*sec(x)^2)^(5/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e49 | verified 0.1s | 3.7s | `(a*sec(x)^2)^(3/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e50 | expected 0.1s | 0.7s | `(a*sec(x)^2)^(1/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e51 | verified 0.2s | 0.4s | `1/(a*sec(x)^2)^(1/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e52 | verified 0.2s | 3.0s | `1/(a*sec(x)^2)^(3/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e53 | verified 0.2s | 4.0s | `1/(a*sec(x)^2)^(5/2)` |
| 4.5.0 (a sec)^m (b trg)^n | e54 | verified 0.3s | 5.5s | `1/(a*sec(x)^2)^(7/2)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e782 | no-answer 0.2s | 0.9s | `(d*sec(e+f*x))^n*(a+b*sec(e+f*x))^(3/2)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e783 | no-answer 0.2s | 0.8s | `(d*sec(e+f*x))^n*(a+b*sec(e+f*x))^(1/2)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e784 | no-answer 0.2s | 0.8s | `(d*sec(e+f*x))^n/(a+b*sec(e+f*x))^(1/2)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e785 | no-answer 0.2s | 0.9s | `(d*sec(e+f*x))^n/(a+b*sec(e+f*x))^(3/2)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e787 | no-answer 0.2s | 0.8s | `(d*sec(e+f*x))^n*(a+b*sec(e+f*x))^m` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e267 | no-answer 0.2s | 25.5s | `(a+b*sec(c+d*x))^n*(e*sin(c+d*x))^m` |
| 4.5.3.1 (a+b sec)^m (d sec)^n (A+B sec) | e478 | no-answer 0.8s | 2.2s | `(c*sec(e+f*x))^n*(a+b*sec(e+f*x))^m*(A+B*sec(e+f*x))` |
| 4.5.7 (d trig)^m (a+b (c sec)^n)^p | e463 | no-answer 0.5s | 1.0s | `(a+b*(c*sec(e+f*x))^n)^p*(d*tan(e+f*x))^m` |
| 4.5.7 (d trig)^m (a+b (c sec)^n)^p | e467 | no-answer 0.7s | 1.9s | `cot(e+f*x)*(a+b*(c*sec(e+f*x))^n)^p` |
| 4.5.7 (d trig)^m (a+b (c sec)^n)^p | e468 | no-answer 2.5s | 3.7s | `cot(e+f*x)^3*(a+b*(c*sec(e+f*x))^n)^p` |
| 4.6.0 (a csc)^m (b trg)^n | e47 | verified 0.1s | 4.0s | `(a*csc(x)^2)^(7/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e48 | verified 0.1s | 3.3s | `(a*csc(x)^2)^(5/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e49 | verified 0.1s | 3.0s | `(a*csc(x)^2)^(3/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e50 | expected 0.1s | 0.2s | `(a*csc(x)^2)^(1/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e51 | verified 0.1s | 0.7s | `1/(a*csc(x)^2)^(1/2)` |
| 4.7.3 (c+d x)^m trig^n trig^p | e170 | no-answer 0.3s | 2.9s | `(c+d*x)^m*cos(a+b*x)*cot(a+b*x)^2` |
| 4.7.3 (c+d x)^m trig^n trig^p | e259 | no-answer 0.2s | 2.0s | `(c+d*x)^m*sin(a+b*x)*tan(a+b*x)^2` |
| 4.7.7 Trig functions | e644 | no-answer 0.1s | 0.2s | `F(c,d,cos(a+b*x),r,s)*sin(a+b*x)` |
| 4.7.7 Trig functions | e645 | no-answer 0.1s | 0.1s | `cos(a+b*x)*F(c,d,sin(a+b*x),r,s)` |
| 4.7.7 Trig functions | e646 | no-answer 0.1s | 0.1s | `F(c,d,tan(a+b*x),r,s)*sec(a+b*x)^2` |
| 4.7.7 Trig functions | e647 | no-answer 0.1s | 0.2s | `csc(a+b*x)^2*F(c,d,cot(a+b*x),r,s)` |
| 4.7.7 Trig functions | e850 | verified 0.1s | 1.2s | `tan(c+d*x)/sqrt(a*sin(c+d*x)^2)` |
| 4.7.7 Trig functions | e851 | verified 0.1s | 1.3s | `cot(c+d*x)/sqrt(a*cos(c+d*x)^2)` |
| 4.7.7 Trig functions | e868 | verified 0.1s | 1.2s | `x*csc(x)*sec(x)/sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e869 | verified 0.1s | 1.4s | `x^2*csc(x)*sec(x)/sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e870 | verified 0.1s | 1.3s | `x^3*csc(x)*sec(x)/sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e874 | verified 0.7s | 0.8s | `x*csc(x)*sec(x)*sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e875 | verified 0.1s | 0.9s | `x^2*csc(x)*sec(x)*sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e876 | verified 0.1s | 1.0s | `x^3*csc(x)*sec(x)*sqrt(a*sec(x)^2)` |
| 4.7.7 Trig functions | e914 | expected 0.1s | 1.4s | `10*x^9*cos(x^5*log(x))-x^10*(x^4+5*x^4*log(x))*sin(x^5*log(x))` |

### rubi unverified (32)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 4.1.0 (a sin)^m (b trg)^n | e304 | verified 0.3s | 5.7s | `cos(e+f*x)^4*(b*sin(e+f*x))^(1/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e305 | verified 0.2s | 2.8s | `cos(e+f*x)^2*(b*sin(e+f*x))^(1/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e309 | verified 0.4s | 4.7s | `cos(e+f*x)^4*(b*sin(e+f*x))^(5/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e310 | verified 0.2s | 2.7s | `cos(e+f*x)^2*(b*sin(e+f*x))^(5/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e314 | verified 0.3s | 4.9s | `cos(e+f*x)^4/(b*sin(e+f*x))^(1/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e315 | verified 0.2s | 2.7s | `cos(e+f*x)^2/(b*sin(e+f*x))^(1/3)` |
| 4.1.0 (a sin)^m (b trg)^n | e320 | verified 0.2s | 2.6s | `cos(e+f*x)^2/(b*sin(e+f*x))^(5/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e310 | verified 0.1s | 0.8s | `x^m*(c*sin(a+b*x)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e318 | verified 0.1s | 0.8s | `x^m*(c*sin(a+b*x^2)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e326 | verified 0.2s | 0.9s | `x^m*(c*sin(a+b*x^n)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e327 | verified 0.1s | 0.9s | `x^3*(c*sin(a+b*x^n)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e328 | verified 0.1s | 0.9s | `x^2*(c*sin(a+b*x^n)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e329 | verified 0.1s | 0.5s | `x*(c*sin(a+b*x^n)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e330 | verified 0.1s | 0.2s | `(c*sin(a+b*x^n)^3)^(1/3)` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e332 | verified 0.1s | 0.8s | `(c*sin(a+b*x^n)^3)^(1/3)/x^2` |
| 4.1.12 (e x)^m (a+b sin(c+d x^n))^p | e333 | verified 0.1s | 0.8s | `(c*sin(a+b*x^n)^3)^(1/3)/x^3` |
| 4.3.1.2 (d sec)^m (a+b tan)^n | e629 | verified 1.0s | 29.2s | `(d*sec(e+f*x))^(1/3)*(a+b*tan(e+f*x))^2` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e280 | verified 0.2s | 1.8s | `(e*sec(c+d*x))^(2/3)/sqrt(a+a*sec(c+d*x))` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e281 | verified 0.2s | 1.9s | `(e*sec(c+d*x))^(1/3)/sqrt(a+a*sec(c+d*x))` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e282 | verified 0.2s | 2.0s | `1/((e*sec(c+d*x))^(1/3)*sqrt(a+a*sec(c+d*x)))` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e21 | verified 3.6s | 0.9s | `sec(c+d*x)^m*(b*sec(c+d*x))^(4/3)*(A+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e22 | verified 1.3s | 0.9s | `sec(c+d*x)^m*(b*sec(c+d*x))^(2/3)*(A+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e23 | verified 1.4s | 0.9s | `sec(c+d*x)^m*(b*sec(c+d*x))^(1/3)*(A+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e24 | verified 1.0s | 1.0s | `sec(c+d*x)^m*(A+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(1/3)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e25 | verified 0.9s | 0.9s | `sec(c+d*x)^m*(A+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(2/3)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e26 | verified 0.8s | 1.0s | `sec(c+d*x)^m*(A+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(4/3)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e65 | verified 6.7s | 1.8s | `sec(c+d*x)^m*(b*sec(c+d*x))^(4/3)*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e66 | verified 2.1s | 1.8s | `sec(c+d*x)^m*(b*sec(c+d*x))^(2/3)*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e67 | verified 2.2s | 2.1s | `sec(c+d*x)^m*(b*sec(c+d*x))^(1/3)*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e68 | verified 1.0s | 1.6s | `sec(c+d*x)^m*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(1/3)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e69 | verified 1.0s | 1.7s | `sec(c+d*x)^m*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(2/3)` |
| 4.5.4.2 (a+b sec)^m (d sec)^n (A+B sec+C sec^2) | e70 | verified 0.9s | 2.1s | `sec(c+d*x)^m*(A+B*sec(c+d*x)+C*sec(c+d*x)^2)/(b*sec(c+d*x))^(4/3)` |

### rubi timeout (29)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e1 | verified 0.1s | 30.1s | `(a*sin(x)^2)^(5/2)` |
| 4.1.7 (d trig)^m (a+b (c sin)^n)^p | e2 | verified 0.1s | 30.1s | `(a*sin(x)^2)^(3/2)` |
| 4.3.1.2 (d sec)^m (a+b tan)^n | e628 | verified 3.0s | 30.0s | `(d*sec(e+f*x))^(5/3)*(a+b*tan(e+f*x))^2` |
| 4.3.1.2 (d sec)^m (a+b tan)^n | e630 | verified 0.6s | 30.0s | `(a+b*tan(e+f*x))^2/(d*sec(e+f*x))^(1/3)` |
| 4.3.1.2 (d sec)^m (a+b tan)^n | e631 | verified 0.5s | 30.1s | `(a+b*tan(e+f*x))^2/(d*sec(e+f*x))^(5/3)` |
| 4.3.1.3 (d sin)^m (a+b tan)^n | e83 | no-answer 0.2s | 30.1s | `sin(c+d*x)^m*(a+b*tan(c+d*x))^n` |
| 4.3.1.3 (d sin)^m (a+b tan)^n | e88 | no-answer 0.3s | 30.1s | `sin(c+d*x)^3*(a+b*tan(c+d*x))^n` |
| 4.3.1.3 (d sin)^m (a+b tan)^n | e89 | no-answer 0.2s | 30.1s | `sin(c+d*x)*(a+b*tan(c+d*x))^n` |
| 4.3.1.3 (d sin)^m (a+b tan)^n | e91 | no-answer 0.3s | 30.1s | `csc(c+d*x)^3*(a+b*tan(c+d*x))^n` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e263 | no-answer 0.2s | 30.0s | `(a+b*sec(c+d*x))^(3/2)*(e*sin(c+d*x))^m` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e264 | no-answer 0.2s | 30.1s | `(a+b*sec(c+d*x))^(1/2)*(e*sin(c+d*x))^m` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e265 | no-answer 0.2s | 30.0s | `(e*sin(c+d*x))^m/(a+b*sec(c+d*x))^(1/2)` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e266 | no-answer 0.3s | 30.1s | `(e*sin(c+d*x))^m/(a+b*sec(c+d*x))^(3/2)` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e277 | no-answer 0.2s | 30.1s | `(a+b*sec(c+d*x))^n*sin(c+d*x)^(3/2)` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e278 | no-answer 0.2s | 30.1s | `(a+b*sec(c+d*x))^n*sin(c+d*x)^(1/2)` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e279 | no-answer 0.2s | 30.0s | `(a+b*sec(c+d*x))^n/sin(c+d*x)^(1/2)` |
| 4.5.1.3 (d sin)^n (a+b sec)^m | e280 | no-answer 0.3s | 30.1s | `(a+b*sec(c+d*x))^n/sin(c+d*x)^(3/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e348 | no-answer 0.3s | 30.0s | `(a+b*sec(c+d*x))^(3/2)*(e*tan(c+d*x))^m` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e349 | no-answer 0.3s | 30.1s | `(a+b*sec(c+d*x))^(1/2)*(e*tan(c+d*x))^m` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e350 | no-answer 0.3s | 30.1s | `(e*tan(c+d*x))^m/(a+b*sec(c+d*x))^(1/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e351 | no-answer 0.3s | 30.1s | `(e*tan(c+d*x))^m/(a+b*sec(c+d*x))^(3/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e352 | no-answer 0.7s | 30.1s | `(a+b*sec(c+d*x))^n*(e*tan(c+d*x))^m` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e362 | no-answer 0.3s | 30.0s | `(a+b*sec(c+d*x))^n*tan(c+d*x)^(3/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e363 | no-answer 0.3s | 30.1s | `(a+b*sec(c+d*x))^n*tan(c+d*x)^(1/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e364 | no-answer 0.3s | 30.1s | `(a+b*sec(c+d*x))^n/tan(c+d*x)^(1/2)` |
| 4.5.1.4 (d tan)^n (a+b sec)^m | e365 | no-answer 0.2s | 30.1s | `(a+b*sec(c+d*x))^n/tan(c+d*x)^(3/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e52 | verified 0.2s | 30.0s | `1/(a*csc(x)^2)^(3/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e53 | verified 0.1s | 30.1s | `1/(a*csc(x)^2)^(5/2)` |
| 4.6.0 (a csc)^m (b trg)^n | e54 | verified 0.2s | 30.1s | `1/(a*csc(x)^2)^(7/2)` |

### rubi deferred (4)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 4.7.7 Trig functions | e49 | expected 0.0s | 0.7s | `x*cos(sqrt(3)*sqrt(2+x^2))/sqrt(2+x^2)` |
| 4.7.7 Trig functions | e749 | expected 0.0s | 0.3s | `csc(x)*log(tan(x))*sec(x)` |
| 4.7.7 Trig functions | e811 | verified 0.0s | 0.2s | `(-3+4*x+x^2)*sin(2*x)` |
| 4.7.7 Trig functions | e920 | verified 0.0s | 0.1s | `(a+b*x+c*x^2)*sin(x)` |

### rubi error (2)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 4.1.0 (a sin)^m (b trg)^n | e319 | verified 0.3s | 17.2s | `cos(e+f*x)^4/(b*sin(e+f*x))^(5/3)` |
| 4.5.1.2 (d sec)^n (a+b sec)^m | e283 | verified 0.2s | 2.5s | `1/((e*sec(c+d*x))^(2/3)*sqrt(a+a*sec(c+d*x)))` |

## Class 5 (108)

### rubi contains-noun (91)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | e16 | verified 0.1s | 7.4s | `(d-c^2*d*x^2)^2*(a+b*asin(c*x))/x^2` |
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | e18 | verified 0.0s | 7.7s | `(d-c^2*d*x^2)^2*(a+b*asin(c*x))/x^4` |
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | e283 | no-answer 0.1s | 7.0s | `x^m*(d-c^2*d*x^2)^(3/2)*(a+b*asin(c*x))^2` |
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | e284 | no-answer 0.1s | 2.3s | `x^m*(d-c^2*d*x^2)^(1/2)*(a+b*asin(c*x))^2` |
| 5.1.4b (f x)^m (d+e x^2)^p (a+b arcsin(c x))^n | e16 | verified 0.0s | 4.9s | `(d+e*x^2)^2*(a+b*asin(c*x))/x^2` |
| 5.1.4b (f x)^m (d+e x^2)^p (a+b arcsin(c x))^n | e18 | verified 0.0s | 4.8s | `(d+e*x^2)^2*(a+b*asin(c*x))/x^4` |
| 5.1.5 Inverse sine functions | e146 | no-answer 0.1s | 0.5s | `1/(x*asin(a+b*x))` |
| 5.1.5 Inverse sine functions | e220 | no-answer 0.1s | 1.0s | `1/((c*e+d*e*x)*(a+b*asin(c+d*x)))` |
| 5.1.5 Inverse sine functions | e244 | no-answer 0.1s | 1.0s | `sqrt(a+b*asin(c+d*x))/(c*e+d*e*x)` |
| 5.1.5 Inverse sine functions | e249 | no-answer 0.1s | 1.1s | `(a+b*asin(c+d*x))^(3/2)/(c*e+d*e*x)` |
| 5.1.5 Inverse sine functions | e254 | no-answer 0.2s | 1.0s | `(a+b*asin(c+d*x))^(5/2)/(c*e+d*e*x)` |
| 5.1.5 Inverse sine functions | e258 | no-answer 0.2s | 1.0s | `(a+b*asin(c+d*x))^(7/2)/(c*e+d*e*x)` |
| 5.1.5 Inverse sine functions | e312 | no-answer 0.1s | 0.5s | `(c*e+d*e*x)^m/(a+b*asin(c+d*x))` |
| 5.1.5 Inverse sine functions | e336 | no-answer 0.1s | 0.7s | `1/((1-a^2-2*a*b*x-b^2*x^2)^(3/2)*asin(a+b*x))` |
| 5.1.5 Inverse sine functions | e466 | expected 0.0s | 0.7s | `%e^asin(a*x)/(1-a^2*x^2)^(1/2)` |
| 5.3.3 (d+e x)^m (a+b arctan(c x^n))^p | e23 | verified 0.2s | 0.6s | `(a+b*atan(c*x^2))/(d+e*x)` |
| 5.3.3 (d+e x)^m (a+b arctan(c x^n))^p | e30 | verified 1.4s | 0.8s | `(a+b*atan(c*x^3))/(d+e*x)` |
| 5.3.4 u (a+b arctan(c x))^p | e61 | verified 0.1s | 9.3s | `x*(a+b*atan(c*x))/(d+%i*c*d*x)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e103 | verified 0.4s | 4.4s | `x^4*(a+b*atan(c*x))^2/(d+%i*c*d*x)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e104 | verified 0.4s | 3.8s | `x^3*(a+b*atan(c*x))^2/(d+%i*c*d*x)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e105 | verified 0.4s | 3.1s | `x^2*(a+b*atan(c*x))^2/(d+%i*c*d*x)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e106 | verified 0.3s | 1.9s | `x*(a+b*atan(c*x))^2/(d+%i*c*d*x)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e114 | verified 0.1s | 1.2s | `x*(a+b*atan(c*x))^2/(d+%i*c*d*x)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e543 | verified 0.1s | 1.1s | `x^3/((c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e544 | verified 0.1s | 1.0s | `x^2/((c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e545 | verified 0.1s | 0.6s | `x/((c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e547 | verified 0.1s | 1.0s | `1/(x*(c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e548 | verified 0.1s | 1.0s | `1/(x^2*(c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e549 | verified 0.1s | 1.0s | `1/(x^3*(c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e550 | verified 0.1s | 1.0s | `1/(x^4*(c+a^2*c*x^2)*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e551 | verified 0.1s | 4.2s | `x^3/((c+a^2*c*x^2)^2*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e555 | verified 0.1s | 4.5s | `1/(x*(c+a^2*c*x^2)^2*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e556 | verified 0.1s | 3.1s | `1/(x^2*(c+a^2*c*x^2)^2*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e557 | verified 0.1s | 6.3s | `1/(x^3*(c+a^2*c*x^2)^2*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e558 | verified 0.1s | 5.0s | `1/(x^4*(c+a^2*c*x^2)^2*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e563 | verified 0.1s | 8.7s | `1/(x*(c+a^2*c*x^2)^3*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e564 | verified 0.1s | 5.8s | `1/(x^2*(c+a^2*c*x^2)^3*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e565 | verified 0.1s | 16.5s | `1/(x^3*(c+a^2*c*x^2)^3*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e566 | verified 0.1s | 11.5s | `1/(x^4*(c+a^2*c*x^2)^3*atan(a*x)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e619 | verified 0.1s | 1.1s | `x^3/((c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e620 | verified 0.1s | 1.0s | `x^2/((c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e621 | verified 0.1s | 0.6s | `x/((c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e623 | verified 0.1s | 1.0s | `1/(x*(c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e624 | verified 0.1s | 1.1s | `1/(x^2*(c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e625 | verified 0.1s | 1.1s | `1/(x^3*(c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e626 | verified 0.1s | 1.1s | `1/(x^4*(c+a^2*c*x^2)*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e627 | verified 0.1s | 3.1s | `x^3/((c+a^2*c*x^2)^2*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e631 | verified 0.1s | 3.5s | `1/(x*(c+a^2*c*x^2)^2*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e632 | verified 0.1s | 5.0s | `1/(x^2*(c+a^2*c*x^2)^2*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e633 | verified 0.1s | 5.3s | `1/(x^3*(c+a^2*c*x^2)^2*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e634 | verified 0.1s | 6.7s | `1/(x^4*(c+a^2*c*x^2)^2*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e639 | verified 0.1s | 9.9s | `1/(x*(c+a^2*c*x^2)^3*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e640 | verified 0.1s | 9.2s | `1/(x^2*(c+a^2*c*x^2)^3*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e641 | verified 0.1s | 16.7s | `1/(x^3*(c+a^2*c*x^2)^3*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e642 | verified 0.1s | 16.8s | `1/(x^4*(c+a^2*c*x^2)^3*atan(a*x)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e1130 | verified 0.0s | 4.5s | `(d+e*x^2)^2*(a+b*atan(c*x))/x^2` |
| 5.3.4 u (a+b arctan(c x))^p | e1132 | verified 0.0s | 4.4s | `(d+e*x^2)^2*(a+b*atan(c*x))/x^4` |
| 5.3.4 u (a+b arctan(c x))^p | e1151 | verified 0.1s | 1.4s | `x^3*(a+b*atan(c*x))/(d+e*x^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1152 | verified 0.1s | 0.8s | `x*(a+b*atan(c*x))/(d+e*x^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1153 | verified 0.1s | 1.6s | `(a+b*atan(c*x))/(x*(d+e*x^2))` |
| 5.3.4 u (a+b arctan(c x))^p | e1154 | verified 0.1s | 2.3s | `(a+b*atan(c*x))/(x^3*(d+e*x^2))` |
| 5.3.4 u (a+b arctan(c x))^p | e1158 | verified 0.1s | 2.2s | `x^3*(a+b*atan(c*x))/(d+e*x^2)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e1160 | verified 0.2s | 2.5s | `(a+b*atan(c*x))/(x*(d+e*x^2)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1161 | verified 0.1s | 2.6s | `(a+b*atan(c*x))/(x^3*(d+e*x^2)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1162 | verified 0.2s | 12.9s | `x^2*(a+b*atan(c*x))/(d+e*x^2)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e1163 | verified 0.2s | 5.1s | `(a+b*atan(c*x))/(d+e*x^2)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e1164 | verified 0.6s | 12.8s | `(a+b*atan(c*x))/(x^2*(d+e*x^2)^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1165 | verified 0.2s | 3.2s | `x^5*(a+b*atan(c*x))/(d+e*x^2)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e1168 | verified 0.3s | 3.5s | `(a+b*atan(c*x))/(x*(d+e*x^2)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e1169 | verified 0.2s | 3.6s | `(a+b*atan(c*x))/(x^3*(d+e*x^2)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e1170 | verified 2.2s | 15.5s | `x^2*(a+b*atan(c*x))/(d+e*x^2)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e1171 | verified 2.2s | 7.3s | `(a+b*atan(c*x))/(d+e*x^2)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e1172 | verified 9.2s | 21.8s | `(a+b*atan(c*x))/(x^2*(d+e*x^2)^3)` |
| 5.3.4 u (a+b arctan(c x))^p | e1209 | verified 0.1s | 2.9s | `x^3*(a+b*atan(c*x))/(d+e*x^2)^(3/2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1261 | verified 0.1s | 2.5s | `x^3*(a+b*atan(c*x))^2/(d+e*x^2)` |
| 5.3.4 u (a+b arctan(c x))^p | e1267 | verified 1.7s | 5.5s | `(a+b*atan(c*x))^2/(x^3*(d+e*x^2))` |
| 5.3.4 u (a+b arctan(c x))^p | e1297 | verified 0.1s | 2.9s | `x*(a+b*atan(c*x))*(d+e*log(f+g*x^2))` |
| 5.3.4 u (a+b arctan(c x))^p | e1299 | verified 0.1s | 2.3s | `(a+b*atan(c*x))*(d+e*log(f+g*x^2))/x` |
| 5.3.4 u (a+b arctan(c x))^p | e1301 | verified 0.1s | 2.4s | `(a+b*atan(c*x))*(d+e*log(f+g*x^2))/x^3` |
| 5.3.5 u (a+b arctan(c+d x))^p | e65 | no-answer 0.1s | 0.6s | `atan(a+b*x)/(1+a^2+2*a*b*x+b^2*x^2)^(1/3)` |
| 5.3.5 u (a+b arctan(c+d x))^p | e66 | no-answer 0.1s | 0.7s | `atan(a+b*x)/((1+a^2)*c+2*a*b*c*x+b^2*c*x^2)^(1/3)` |
| 5.3.5 u (a+b arctan(c+d x))^p | e69 | no-answer 0.1s | 1.7s | `(a+b*x)^2*atan(a+b*x)/(1+a^2+2*a*b*x+b^2*x^2)^(1/3)` |
| 5.3.5 u (a+b arctan(c+d x))^p | e70 | no-answer 0.1s | 1.7s | `(a+b*x)^2*atan(a+b*x)/((1+a^2)*c+2*a*b*c*x+b^2*c*x^2)^(1/3)` |
| 5.4.1 Inverse cotangent functions | e116 | no-answer 0.1s | 0.6s | `acot(a+b*x)/(1+a^2+2*a*b*x+b^2*x^2)^(1/3)` |
| 5.4.1 Inverse cotangent functions | e117 | no-answer 0.1s | 0.7s | `acot(a+b*x)/((1+a^2)*c+2*a*b*c*x+b^2*c*x^2)^(1/3)` |
| 5.4.1 Inverse cotangent functions | e120 | no-answer 0.1s | 1.7s | `(a+b*x)^2*acot(a+b*x)/(1+a^2+2*a*b*x+b^2*x^2)^(1/3)` |
| 5.4.1 Inverse cotangent functions | e121 | no-answer 0.1s | 1.7s | `(a+b*x)^2*acot(a+b*x)/((1+a^2)*c+2*a*b*c*x+b^2*c*x^2)^(1/3)` |
| 5.5.1 u (a+b arcsec(c x))^n | e83 | verified 0.0s | 7.1s | `(d+e*x^2)^2*(a+b*asec(c*x))/x^2` |
| 5.5.1 u (a+b arcsec(c x))^n | e84 | verified 0.0s | 6.9s | `(d+e*x^2)^2*(a+b*asec(c*x))/x^4` |
| 5.6.1 u (a+b arccsc(c x))^n | e90 | verified 0.1s | 6.9s | `(d+e*x^2)^2*(a+b*acsc(c*x))/x^2` |
| 5.6.1 u (a+b arccsc(c x))^n | e91 | verified 0.1s | 7.0s | `(d+e*x^2)^2*(a+b*acsc(c*x))/x^4` |

### rubi timeout (12)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 5.1.4a (f x)^m (d-c^2 d x^2)^p (a+b arcsin(c x))^n | e282 | no-answer 0.2s | 30.1s | `x^m*(d-c^2*d*x^2)^(5/2)*(a+b*asin(c*x))^2` |
| 5.1.5 Inverse sine functions | e98 | verified 0.1s | 30.1s | `(d+e*x)^2*(f+g*x+h*x^2)*(a+b*asin(c*x))` |
| 5.1.5 Inverse sine functions | e350 | verified 0.0s | 30.1s | `(a+b*asin(c*x^2))/x^11` |
| 5.3.3 (d+e x)^m (a+b arctan(c x^n))^p | e24 | verified 0.1s | 30.1s | `(a+b*atan(c*x^2))/(d+e*x)^2` |
| 5.3.4 u (a+b arctan(c x))^p | e379 | verified 0.8s | 30.1s | `x^3*(c+a^2*c*x^2)^3*atan(a*x)^3` |
| 5.3.5 u (a+b arctan(c+d x))^p | e30 | verified 0.1s | 30.0s | `(a+b*atan(c+d*x))/(e+f*x)^3` |
| 5.3.6 Exponentials of inverse tangent | e376 | expected 0.1s | 30.1s | `%e^(4*%i*atan(a*x))*x^2/(c+a^2*c*x^2)^9` |
| 5.3.6 Exponentials of inverse tangent | e379 | expected 0.1s | 30.1s | `x^2/(%e^(4*%i*atan(a*x))*(c+a^2*c*x^2)^9)` |
| 5.4.1 Inverse cotangent functions | e135 | verified 0.1s | 30.1s | `(a+b*acot(c+d*x))/(e+f*x)^3` |
| 5.5.2 Inverse secant functions | e8 | verified 0.1s | 30.1s | `asec(sqrt(x))/x^3` |
| 5.5.2 Inverse secant functions | e9 | verified 0.1s | 30.1s | `asec(sqrt(x))/x^4` |
| 5.6.2 Inverse cosecant functions | e8 | verified 0.1s | 30.0s | `acsc(sqrt(x))/x^3` |

### rubi deferred (5)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 5.3.4 u (a+b arctan(c x))^p | e115 | verified 0.1s | 0.3s | `(a+b*atan(c*x))^2/(d+%i*c*d*x)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e118 | verified 0.1s | 0.3s | `(a+b*atan(c*x))^2/(1+%i*c*x)^4` |
| 5.3.4 u (a+b arctan(c x))^p | e125 | verified 0.1s | 0.3s | `(a+b*atan(c*x))^3/(d+%i*c*d*x)^3` |
| 5.3.4 u (a+b arctan(c x))^p | e126 | verified 0.1s | 0.3s | `(a+b*atan(c*x))^3/(d+%i*c*d*x)^4` |
| 5.3.4 u (a+b arctan(c x))^p | e1263 | verified 1.7s | 0.7s | `x*(a+b*atan(c*x))^2/(d+e*x^2)` |

## Class 6 (61)

### rubi contains-noun (44)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 6.1.1 (c+d x)^m (a+b sinh)^n | e26 | no-answer 0.1s | 0.4s | `csch(a+b*x)/(c+d*x)` |
| 6.1.1 (c+d x)^m (a+b sinh)^n | e27 | no-answer 0.1s | 0.7s | `csch(a+b*x)/(c+d*x)^2` |
| 6.1.1 (c+d x)^m (a+b sinh)^n | e72 | no-answer 0.1s | 1.2s | `(c+d*x)^m*(b*sinh(e+f*x))^n` |
| 6.1.3 (e x)^m (a+b sinh(c+d x^n))^p | e92 | no-answer 0.2s | 0.3s | `sinh((a+b*x)^2)/x^2` |
| 6.1.5 Hyperbolic sine functions | e142 | verified 0.0s | 1.6s | `(a*sinh(x)^2)^(1/2)` |
| 6.1.5 Hyperbolic sine functions | e143 | verified 0.1s | 1.6s | `1/(a*sinh(x)^2)^(1/2)` |
| 6.1.5 Hyperbolic sine functions | e144 | verified 0.1s | 3.4s | `1/(a*sinh(x)^2)^(3/2)` |
| 6.1.5 Hyperbolic sine functions | e145 | verified 0.1s | 5.5s | `1/(a*sinh(x)^2)^(5/2)` |
| 6.2.3 (e x)^m (a+b cosh(c+d x^n))^p | e44 | verified 0.1s | 1.0s | `(e*x)^(-1+2*n)*(b*cosh(c+d*x^n))^p` |
| 6.2.3 (e x)^m (a+b cosh(c+d x^n))^p | e58 | no-answer 0.4s | 0.3s | `cosh((a+b*x)^2)/x^2` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e22 | no-answer 0.3s | 1.4s | `(c+d*x)^2*(b*tanh(e+f*x))^(1/2)` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e23 | no-answer 0.4s | 1.4s | `(c+d*x)^2/(b*tanh(e+f*x))^(1/2)` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e25 | no-answer 0.1s | 1.4s | `(b*tanh(e+f*x))^(3/2)/(c+d*x)` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e26 | no-answer 0.2s | 1.5s | `(b*tanh(e+f*x))^(1/2)/(c+d*x)` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e27 | no-answer 0.2s | 1.4s | `1/((c+d*x)*(b*tanh(e+f*x))^(1/2))` |
| 6.3.1 (c+d x)^m (a+b tanh)^n | e28 | no-answer 0.3s | 1.4s | `1/((c+d*x)*(b*tanh(e+f*x))^(3/2))` |
| 6.3.2 Hyperbolic tangent functions | e24 | verified 0.2s | 1.3s | `(a*tanh(x)^2)^(3/2)` |
| 6.3.2 Hyperbolic tangent functions | e25 | verified 0.1s | 0.7s | `sqrt(a*tanh(x)^2)` |
| 6.3.2 Hyperbolic tangent functions | e26 | verified 0.1s | 0.7s | `1/sqrt(a*tanh(x)^2)` |
| 6.3.2 Hyperbolic tangent functions | e27 | verified 0.3s | 2.1s | `(-tanh(c+d*x)^2)^(5/2)` |
| 6.3.2 Hyperbolic tangent functions | e28 | verified 0.2s | 1.9s | `(-tanh(c+d*x)^2)^(3/2)` |
| 6.3.2 Hyperbolic tangent functions | e29 | verified 0.1s | 0.5s | `(-tanh(c+d*x)^2)^(1/2)` |
| 6.3.2 Hyperbolic tangent functions | e30 | verified 0.1s | 0.6s | `1/(-tanh(c+d*x)^2)^(1/2)` |
| 6.3.2 Hyperbolic tangent functions | e31 | verified 0.2s | 3.0s | `1/(-tanh(c+d*x)^2)^(3/2)` |
| 6.3.2 Hyperbolic tangent functions | e32 | verified 0.2s | 3.1s | `1/(-tanh(c+d*x)^2)^(5/2)` |
| 6.4.2 Hyperbolic cotangent functions | e17 | verified 0.1s | 1.0s | `(b*coth(c+d*x)^2)^n` |
| 6.4.2 Hyperbolic cotangent functions | e18 | verified 0.3s | 1.6s | `(b*coth(c+d*x)^2)^(3/2)` |
| 6.4.2 Hyperbolic cotangent functions | e19 | verified 0.2s | 0.7s | `(b*coth(c+d*x)^2)^(1/2)` |
| 6.4.2 Hyperbolic cotangent functions | e20 | verified 0.1s | 0.6s | `1/(b*coth(c+d*x)^2)^(1/2)` |
| 6.4.2 Hyperbolic cotangent functions | e21 | verified 0.4s | 1.6s | `1/(b*coth(c+d*x)^2)^(3/2)` |
| 6.4.2 Hyperbolic cotangent functions | e39 | verified 0.1s | 1.0s | `(b*coth(c+d*x)^4)^n` |
| 6.6.3 Hyperbolic cosecant functions | e22 | verified 0.1s | 5.3s | `(-csch(x)^2)^(5/2)` |
| 6.6.3 Hyperbolic cosecant functions | e23 | verified 0.1s | 3.0s | `(-csch(x)^2)^(3/2)` |
| 6.6.3 Hyperbolic cosecant functions | e24 | verified 0.1s | 1.5s | `(-csch(x)^2)^(1/2)` |
| 6.6.3 Hyperbolic cosecant functions | e25 | verified 0.1s | 1.7s | `1/(-csch(x)^2)^(1/2)` |
| 6.6.3 Hyperbolic cosecant functions | e29 | verified 0.1s | 5.6s | `(a*csch(x)^2)^(5/2)` |
| 6.6.3 Hyperbolic cosecant functions | e30 | verified 0.1s | 3.0s | `(a*csch(x)^2)^(3/2)` |
| 6.6.3 Hyperbolic cosecant functions | e31 | expected 0.1s | 1.5s | `(a*csch(x)^2)^(1/2)` |
| 6.6.3 Hyperbolic cosecant functions | e32 | verified 0.1s | 1.6s | `1/(a*csch(x)^2)^(1/2)` |
| 6.7.1 Hyperbolic functions | e1014 | no-answer 0.1s | 0.1s | `cosh(a+b*x)*F(c,d,sinh(a+b*x),r,s)` |
| 6.7.1 Hyperbolic functions | e1015 | no-answer 0.1s | 0.1s | `F(c,d,cosh(a+b*x),r,s)*sinh(a+b*x)` |
| 6.7.1 Hyperbolic functions | e1016 | no-answer 0.1s | 0.2s | `F(c,d,tanh(a+b*x),r,s)*sech(a+b*x)^2` |
| 6.7.1 Hyperbolic functions | e1017 | no-answer 0.1s | 0.2s | `csch(a+b*x)^2*F(c,d,coth(a+b*x),r,s)` |
| 6.7.1 Hyperbolic functions | e1037 | verified 0.1s | 2.0s | `tanh(c+d*x)/sqrt(a*sinh(c+d*x)^2)` |

### rubi timeout (8)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 6.1.5 Hyperbolic sine functions | e140 | verified 0.1s | 30.1s | `(a*sinh(x)^2)^(5/2)` |
| 6.1.5 Hyperbolic sine functions | e141 | verified 0.1s | 30.1s | `(a*sinh(x)^2)^(3/2)` |
| 6.6.3 Hyperbolic cosecant functions | e26 | verified 0.1s | 30.1s | `1/(-csch(x)^2)^(3/2)` |
| 6.6.3 Hyperbolic cosecant functions | e27 | verified 0.1s | 30.1s | `1/(-csch(x)^2)^(5/2)` |
| 6.6.3 Hyperbolic cosecant functions | e28 | verified 0.1s | 30.1s | `1/(-csch(x)^2)^(7/2)` |
| 6.6.3 Hyperbolic cosecant functions | e33 | verified 0.1s | 30.1s | `1/(a*csch(x)^2)^(3/2)` |
| 6.6.3 Hyperbolic cosecant functions | e34 | verified 0.2s | 30.1s | `1/(a*csch(x)^2)^(5/2)` |
| 6.6.3 Hyperbolic cosecant functions | e35 | verified 0.1s | 30.1s | `1/(a*csch(x)^2)^(7/2)` |

### rubi unverified (8)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 6.4.2 Hyperbolic cotangent functions | e9 | verified 0.1s | 0.8s | `(b*coth(c+d*x))^(4/3)` |
| 6.4.2 Hyperbolic cotangent functions | e23 | verified 0.3s | 0.8s | `(b*coth(c+d*x)^2)^(2/3)` |
| 6.4.2 Hyperbolic cotangent functions | e27 | verified 0.3s | 0.9s | `1/(b*coth(c+d*x)^2)^(4/3)` |
| 6.4.2 Hyperbolic cotangent functions | e44 | verified 0.2s | 15.9s | `(b*coth(c+d*x)^4)^(4/3)` |
| 6.4.2 Hyperbolic cotangent functions | e45 | verified 0.2s | 2.5s | `(b*coth(c+d*x)^4)^(2/3)` |
| 6.4.2 Hyperbolic cotangent functions | e46 | verified 0.2s | 0.9s | `(b*coth(c+d*x)^4)^(1/3)` |
| 6.4.2 Hyperbolic cotangent functions | e48 | verified 0.1s | 0.8s | `1/(b*coth(c+d*x)^4)^(2/3)` |
| 6.4.2 Hyperbolic cotangent functions | e49 | verified 0.2s | 14.4s | `1/(b*coth(c+d*x)^4)^(4/3)` |

### rubi deferred (1)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 6.7.1 Hyperbolic functions | e1013 | expected 0.0s | 0.2s | `csch(2*x)*log(tanh(x))` |

## Class 7 (41)

### rubi contains-noun (30)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | e16 | verified 0.0s | 7.5s | `(d+c^2*d*x^2)^2*(a+b*asinh(c*x))/x^2` |
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | e18 | verified 0.0s | 7.4s | `(d+c^2*d*x^2)^2*(a+b*asinh(c*x))/x^4` |
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | e251 | no-answer 0.1s | 6.4s | `x^m*(d+c^2*d*x^2)^(3/2)*(a+b*asinh(c*x))^2` |
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | e252 | no-answer 0.1s | 2.1s | `x^m*(d+c^2*d*x^2)^(1/2)*(a+b*asinh(c*x))^2` |
| 7.1.5 Inverse hyperbolic sine functions | e84 | no-answer 0.1s | 0.5s | `1/(x*asinh(a+b*x))` |
| 7.1.5 Inverse hyperbolic sine functions | e155 | no-answer 0.1s | 0.5s | `(c*e+d*e*x)^m/(a+b*asinh(c+d*x))` |
| 7.1.5 Inverse hyperbolic sine functions | e161 | no-answer 0.1s | 1.0s | `1/((c*e+d*e*x)*(a+b*asinh(c+d*x)))` |
| 7.1.5 Inverse hyperbolic sine functions | e281 | no-answer 0.1s | 0.8s | `1/((1+a^2+2*a*b*x+b^2*x^2)^(3/2)*asinh(a+b*x))` |
| 7.2.4a (f x)^m (d-c^2 d x^2)^p (a+b arccosh(c x))^n | e16 | verified 0.0s | 7.5s | `(d-c^2*d*x^2)^2*(a+b*acosh(c*x))/x^2` |
| 7.2.4a (f x)^m (d-c^2 d x^2)^p (a+b arccosh(c x))^n | e18 | verified 0.1s | 7.5s | `(d-c^2*d*x^2)^2*(a+b*acosh(c*x))/x^4` |
| 7.2.4b (f x)^m (d+e x^2)^p (a+b arccosh(c x))^n | e16 | verified 0.1s | 7.7s | `(d+e*x^2)^2*(a+b*acosh(c*x))/x^2` |
| 7.2.4b (f x)^m (d+e x^2)^p (a+b arccosh(c x))^n | e18 | verified 0.1s | 7.3s | `(d+e*x^2)^2*(a+b*acosh(c*x))/x^4` |
| 7.2.5 Inverse hyperbolic cosine functions | e132 | no-answer 0.1s | 1.0s | `1/((c*e+d*e*x)*(a+b*acosh(c+d*x)))` |
| 7.2.5 Inverse hyperbolic cosine functions | e227 | no-answer 0.1s | 0.5s | `(c*e+d*e*x)^m/(a+b*acosh(c+d*x))` |
| 7.2.5 Inverse hyperbolic cosine functions | e229 | verified 0.0s | 2.8s | `x^2*acosh(sqrt(x))` |
| 7.2.5 Inverse hyperbolic cosine functions | e230 | verified 0.0s | 2.7s | `x*acosh(sqrt(x))` |
| 7.2.5 Inverse hyperbolic cosine functions | e231 | verified 0.0s | 2.8s | `acosh(sqrt(x))` |
| 7.2.5 Inverse hyperbolic cosine functions | e233 | verified 0.0s | 3.1s | `acosh(sqrt(x))/x^2` |
| 7.2.5 Inverse hyperbolic cosine functions | e234 | verified 0.0s | 2.7s | `acosh(sqrt(x))/x^3` |
| 7.3.4 u (a+b arctanh(c x))^p | e114 | verified 0.1s | 3.6s | `x*(a+b*atanh(c*x))^2/(d+c*d*x)^3` |
| 7.3.4 u (a+b arctanh(c x))^p | e115 | verified 0.1s | 2.5s | `(a+b*atanh(c*x))^2/(d+c*d*x)^3` |
| 7.3.4 u (a+b arctanh(c x))^p | e118 | verified 0.1s | 3.7s | `(a+b*atanh(c*x))^2/(1+c*x)^4` |
| 7.3.4 u (a+b arctanh(c x))^p | e124 | verified 0.1s | 3.6s | `(a+b*atanh(c*x))^3/(1+c*x)^2` |
| 7.3.4 u (a+b arctanh(c x))^p | e125 | verified 0.1s | 8.2s | `(a+b*atanh(c*x))^3/(1+c*x)^3` |
| 7.3.4 u (a+b arctanh(c x))^p | e126 | verified 0.1s | 24.2s | `(a+b*atanh(c*x))^3/(1+c*x)^4` |
| 7.5.1 u (a+b arcsech(c x))^n | e102 | verified 0.1s | 10.3s | `(d+e*x^2)^2*(a+b*asech(c*x))/x^2` |
| 7.5.1 u (a+b arcsech(c x))^n | e103 | verified 0.1s | 10.2s | `(d+e*x^2)^2*(a+b*asech(c*x))/x^4` |
| 7.5.2 Inverse hyperbolic secant functions | e97 | expected 0.1s | 2.4s | `x*(-1+%e^asech(a*x)*a*x)/(1-a^2*x^2)` |
| 7.6.1 u (a+b arccsch(c x))^n | e90 | verified 0.1s | 7.2s | `(d+e*x^2)^2*(a+b*acsch(c*x))/x^2` |
| 7.6.1 u (a+b arccsch(c x))^n | e91 | verified 0.1s | 7.9s | `(d+e*x^2)^2*(a+b*acsch(c*x))/x^4` |

### rubi timeout (10)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 7.1.4a (f x)^m (d+c^2 d x^2)^p (a+b arcsinh(c x))^n | e250 | no-answer 0.1s | 30.0s | `x^m*(d+c^2*d*x^2)^(5/2)*(a+b*asinh(c*x))^2` |
| 7.3.4 u (a+b arctanh(c x))^p | e33 | verified 0.1s | 30.0s | `x*(d+c*d*x)^4*(a+b*atanh(c*x))` |
| 7.3.6 Exponentials of inverse hyperbolic tangent functions | e1369 | expected 0.1s | 30.0s | `%e^(4*atanh(a*x))*x^2/(c-a^2*c*x^2)^9` |
| 7.3.6 Exponentials of inverse hyperbolic tangent functions | e1372 | expected 0.1s | 30.0s | `x^2/(%e^(4*atanh(a*x))*(c-a^2*c*x^2)^9)` |
| 7.5.1 u (a+b arcsech(c x))^n | e32 | verified 0.1s | 30.0s | `(a+b*asech(c*x))/x^7` |
| 7.5.1 u (a+b arcsech(c x))^n | e106 | verified 0.1s | 30.1s | `x^3*(d+e*x^2)^2*(a+b*asech(c*x))` |
| 7.5.2 Inverse hyperbolic secant functions | e26 | verified 0.1s | 30.1s | `asech(sqrt(x))/x^3` |
| 7.5.2 Inverse hyperbolic secant functions | e27 | verified 0.1s | 30.1s | `asech(sqrt(x))/x^4` |
| 7.6.2 Inverse hyperbolic cosecant functions | e20 | verified 0.1s | 30.1s | `acsch(sqrt(x))/x^3` |
| 7.6.2 Inverse hyperbolic cosecant functions | e21 | verified 0.1s | 30.1s | `acsch(sqrt(x))/x^4` |

### rubi error (1)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 7.3.6 Exponentials of inverse hyperbolic tangent functions | e1368 | expected 0.2s | 20.6s | `%e^(6*atanh(a*x))*x^2/(c-a^2*c*x^2)^19` |

## Class 8 (27)

### rubi contains-noun (27)

| file | entry | integrate | rubi | integrand |
|---|---|---|---|---|
| 8.1 Error functions | e20 | verified 0.1s | 0.7s | `erf(a+b*x)/(c+d*x)^2` |
| 8.1 Error functions | e21 | verified 0.1s | 1.0s | `erf(a+b*x)/(c+d*x)^3` |
| 8.10 Formal derivatives | e42 | no-answer 0.1s | 1.2s | `(g(x)*Derivative(1)(f)(x)+f(x)*Derivative(1)(g)(x))/(a+b*f(x)^n*g(x)^n)` |
| 8.10 Formal derivatives | e49 | no-answer 0.1s | 0.4s | `F^(a+b*x)*Derivative(-2)(f)(x)` |
| 8.10 Formal derivatives | e56 | no-answer 0.1s | 0.2s | `sin(a+b*x)*Derivative(-1)(f)(x)` |
| 8.10 Formal derivatives | e66 | no-answer 0.1s | 0.3s | `cos(a+b*x)*Derivative(-3)(f)(x)` |
| 8.3 Exponential integral functions | e167 | no-answer 0.1s | 0.1s | `Ei(a+b*x)^3` |
| 8.9 Product logarithm function | e41 | no-answer 0.1s | 0.5s | `1/(x*sqrt(c*ProductLog(a+b*x)))` |
| 8.9 Product logarithm function | e42 | no-answer 0.1s | 0.6s | `1/(x^2*sqrt(c*ProductLog(a+b*x)))` |
| 8.9 Product logarithm function | e47 | no-answer 0.1s | 0.5s | `1/(x*sqrt(-c*ProductLog(a+b*x)))` |
| 8.9 Product logarithm function | e48 | no-answer 0.1s | 0.6s | `1/(x^2*sqrt(-c*ProductLog(a+b*x)))` |
| 8.9 Product logarithm function | e53 | no-answer 0.1s | 0.5s | `sqrt(c*ProductLog(a+b*x))/x` |
| 8.9 Product logarithm function | e54 | no-answer 0.1s | 0.5s | `sqrt(c*ProductLog(a+b*x))/x^2` |
| 8.9 Product logarithm function | e220 | no-answer 0.1s | 0.5s | `sqrt(c*ProductLog(a*x^2))/x^2` |
| 8.9 Product logarithm function | e222 | no-answer 0.1s | 0.5s | `sqrt(c*ProductLog(a*x^2))/x^4` |
| 8.9 Product logarithm function | e224 | no-answer 0.1s | 0.5s | `sqrt(c*ProductLog(a*x^2))/x^6` |
| 8.9 Product logarithm function | e233 | no-answer 0.1s | 0.1s | `1/sqrt(c*ProductLog(a*x^2))` |
| 8.9 Product logarithm function | e235 | no-answer 0.1s | 0.5s | `1/(x^2*sqrt(c*ProductLog(a*x^2)))` |
| 8.9 Product logarithm function | e237 | no-answer 0.1s | 0.6s | `1/(x^4*sqrt(c*ProductLog(a*x^2)))` |
| 8.9 Product logarithm function | e239 | no-answer 0.1s | 0.6s | `1/(x^6*sqrt(c*ProductLog(a*x^2)))` |
| 8.9 Product logarithm function | e241 | no-answer 0.1s | 0.6s | `x^2*(c*ProductLog(a*x^2))^p` |
| 8.9 Product logarithm function | e244 | no-answer 0.1s | 0.5s | `(c*ProductLog(a*x^2))^p/x^2` |
| 8.9 Product logarithm function | e376 | no-answer 0.1s | 0.6s | `x^4/(1+ProductLog(a/x^2))` |
| 8.9 Product logarithm function | e377 | no-answer 0.1s | 0.5s | `x^2/(1+ProductLog(a/x^2))` |
| 8.9 Product logarithm function | e378 | no-answer 0.1s | 0.4s | `1/(1+ProductLog(a/x^2))` |
| 8.9 Product logarithm function | e379 | no-answer 0.1s | 0.3s | `1/(x^2*(1+ProductLog(a/x^2)))` |
| 8.9 Product logarithm function | e380 | no-answer 0.1s | 0.5s | `1/(x^4*(1+ProductLog(a/x^2)))` |
