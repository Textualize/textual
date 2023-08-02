; -- Keywords
[
	(kProgram)
	(kLibrary)
	(kUnit)

	(kBegin)
	(kEnd)
	(kAsm)

	(kVar)
	(kThreadvar)
	(kConst)
	(kConstref)
	(kResourcestring)
	(kOut)
	(kType)
	(kLabel)
	(kExports)

	(kProperty)
	(kRead)
	(kWrite)
	(kImplements)

	(kClass)
	(kInterface)
	(kObject)
	(kRecord)
	(kObjcclass)
	(kObjccategory)
	(kObjcprotocol)
	(kArray)
	(kFile)
	(kString)
	(kSet)
	(kOf)
	(kHelper)

	(kInherited)

	(kGeneric)
	(kSpecialize)

	(kFunction)
	(kProcedure)
	(kConstructor)
	(kDestructor)
	(kOperator)
	(kReference)

	(kInterface)
	(kImplementation)
	(kInitialization)
	(kFinalization)

	(kTry)
	(kExcept)
	(kFinally)
	(kRaise)
	(kOn)
	(kCase)
	(kWith)
	(kGoto)
] @keyword

[
	(kFor)
	(kTo)
	(kDownto)
	(kDo)
	(kWhile)
	(kRepeat)
	(kUntil)
] @repeat

[
	(kIf)
	(kThen)
	(kElse)
] @conditional

[
	(kPublished)
	(kPublic)
	(kProtected)
	(kPrivate)

	(kStrict)
	(kRequired)
	(kOptional)
] @type.qualifier

[
	(kPacked)

	(kAbsolute)
] @storageclass

(kUses) @include

; -- Attributes

[
	(kDefault)
	(kIndex)
	(kNodefault)
	(kStored)

	(kStatic)
	(kVirtual)
	(kAbstract)
	(kSealed)
	(kDynamic)
	(kOverride)
	(kOverload)
	(kReintroduce)
	(kInline)

	(kForward)

	(kStdcall)
	(kCdecl)
	(kCppdecl)
	(kPascal)
	(kRegister)
	(kMwpascal)
	(kExternal)
	(kName)
	(kMessage)
	(kDeprecated)
	(kExperimental)
	(kPlatform)
	(kUnimplemented)
	(kCvar)
	(kExport)
	(kFar)
	(kNear)
	(kSafecall)
	(kAssembler)
	(kNostackframe)
	(kInterrupt)
	(kNoreturn)
	(kIocheck)
	(kLocal)
	(kHardfloat)
	(kSoftfloat)
	(kMs_abi_default)
	(kMs_abi_cdecl)
	(kSaveregisters)
	(kSysv_abi_default)
	(kSysv_abi_cdecl)
	(kVectorcall)
	(kVarargs)
	(kWinapi)
	(kAlias)
	(kDelayed)

	(rttiAttributes)
	(procAttribute)

] @attribute

(procAttribute (kPublic) @attribute)

; -- Punctuation & operators

[
	"("
	")"
	"["
	"]"
] @punctuation.bracket

[
	";"
	","
	":"
	(kEndDot)
] @punctuation.delimiter

[
	".."
] @punctuation.special

[
	(kDot)
	(kAdd)
	(kSub)
	(kMul)
	(kFdiv)
	(kAssign)
	(kAssignAdd)
	(kAssignSub)
	(kAssignMul)
	(kAssignDiv)
	(kEq)
	(kLt)
	(kLte)
	(kGt)
	(kGte)
	(kNeq)
	(kAt)
	(kHat)
] @operator

[
	(kOr)
	(kXor)
	(kDiv)
	(kMod)
	(kAnd)
	(kShl)
	(kShr)
	(kNot)
	(kIs)
	(kAs)
	(kIn)
] @keyword.operator

; -- Builtin constants

[
	(kTrue)
	(kFalse)
] @boolean

[
	(kNil)
] @constant.builtin

; -- Literals

(literalNumber)   @number
(literalString)   @string

; -- Variables

(exprBinary (identifier) @variable)
(exprUnary (identifier) @variable)
(assignment (identifier) @variable)
(exprBrackets (identifier) @variable)
(exprParens (identifier) @variable)
(exprDot (identifier) @variable)
(exprTpl (identifier) @variable)
(exprArgs (identifier) @variable)
(defaultValue (identifier) @variable)

; -- Comments

(comment) @comment @spell

((comment) @comment.documentation
  (#lua-match? @comment.documentation "^///[^/]"))
((comment) @comment.documentation
  (#lua-match? @comment.documentation "^///$"))

((comment) @comment.documentation
  . [(unit) (declProc)])

(declTypes
  (comment) @comment.documentation
  . (declType))

(declSection
  (comment) @comment.documentation
  . [(declField) (declProc)])

(declEnum
  (comment) @comment.documentation
  . (declEnumValue))

(declConsts
  (comment) @comment.documentation
  . (declConst))

(declVars
  (comment) @comment.documentation
  . (declVar))

(pp)              @preproc

; -- Type declaration

(declType name: (identifier) @type)
(declType name: (genericTpl entity: (identifier) @type))

; -- Procedure & function declarations

; foobar
(declProc name: (identifier) @function)
; foobar<t>
(declProc name: (genericTpl entity: (identifier) @function))
; foo.bar
(declProc name: (genericDot rhs: (identifier) @function))
; foo.bar<t>
(declProc name: (genericDot rhs: (genericTpl entity: (identifier) @function)))

; Treat property declarations like functions

(declProp name: (identifier) @function)
(declProp getter: (identifier) @property)
(declProp setter: (identifier) @property)

; -- Function parameters

(declArg name: (identifier) @parameter)

; -- Template parameters

(genericArg	name: (identifier) @parameter)
(genericArg	type: (typeref) @type)

(declProc name: (genericDot lhs: (identifier) @type))
(declType (genericDot (identifier) @type))

(genericDot (genericTpl (identifier) @type))
(genericDot (genericDot (identifier) @type))

(genericTpl entity: (identifier) @type)
(genericTpl entity: (genericDot (identifier) @type))

; -- Exception parameters

(exceptionHandler variable: (identifier) @parameter)

; -- Type usage

(typeref) @type

; -- Constant usage

[
	(caseLabel)
	(label)
] @constant

(procAttribute (identifier) @constant)
(procExternal (identifier) @constant)

; -- Variable & constant declarations
; (This is only questionable because we cannot detect types of identifiers
; declared in other units, so the results will be inconsistent)

(declVar name: (identifier) @variable)
(declConst name: (identifier) @constant)
(declEnumValue name: (identifier) @constant)

; -- Fields

(exprDot rhs: (identifier) @property)
(exprDot rhs: (exprDot)    @property)
(declClass   (declField name:(identifier) @property))
(declSection (declField name:(identifier) @property))
(declSection (declVars (declVar   name:(identifier) @property)))

(recInitializerField name:(identifier) @property)


;;; ---------------------------------------------- ;;;
;;; EVERYTHING BELOW THIS IS OF QUESTIONABLE VALUE ;;;
;;; ---------------------------------------------- ;;;


; -- Procedure name in calls with parentheses
; (Pascal doesn't require parentheses for procedure calls, so this will not
; detect all calls)

; foobar
(exprCall entity: (identifier) @function)
; foobar<t>
(exprCall entity: (exprTpl entity: (identifier) @function))
; foo.bar
(exprCall entity: (exprDot rhs: (identifier) @function))
; foo.bar<t>
(exprCall entity: (exprDot rhs: (exprTpl entity: (identifier) @function)))

(inherited) @function

; -- Heuristic for procedure/function calls without parentheses
; (If a statement consists only of an identifier, assume it's a procedure)
; (This will still not match all procedure calls, and also may produce false
; positives in rare cases, but only for nonsensical code)

(statement (identifier) @function)
(statement (exprDot rhs: (identifier) @function))
(statement (exprTpl entity: (identifier) @function))
(statement (exprDot rhs: (exprTpl entity: (identifier) @function)))

; -- Break, Continue & Exit
; (Not ideal: ideally, there would be a way to check if these special
; identifiers are shadowed by a local variable)
(statement ((identifier) @keyword.return
 (#lua-match? @keyword.return "^[eE][xX][iI][tT]$")))
(statement (exprCall entity: ((identifier) @keyword.return
 (#lua-match? @keyword.return "^[eE][xX][iI][tT]$"))))
(statement ((identifier) @repeat
 (#lua-match? @repeat "^[bB][rR][eE][aA][kK]$")))
(statement ((identifier) @repeat
 (#lua-match? @repeat "^[cC][oO][nN][tT][iI][nN][uU][eE]$")))

; -- Identifier type inference

; VERY QUESTIONABLE: Highlighting of identifiers based on spelling
(exprBinary ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprUnary ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(assignment rhs: ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprBrackets ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprParens ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprDot rhs: ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprTpl args: ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(exprArgs ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(declEnumValue ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
(defaultValue ((identifier) @constant
 (#match? @constant "^[A-Z][A-Z0-9_]+$|^[a-z]{2,3}[A-Z].+$")))
