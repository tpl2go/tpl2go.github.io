
class CompositeSymbol {
    constructor(left, right, compsymbID) {
        this.left = left;
        this.right = right;
        this.locs = new Set();
        let leftStr = this.left instanceof CompositeSymbol ? this.left.strrepr : String(this.left);
        let rightStr = this.right instanceof CompositeSymbol ? this.right.strrepr : String(this.right);
        this.strrepr = leftStr + rightStr;
        this.length = this.strrepr.length;
        this.compositesymbolID = compsymbID;

        this.toplevelcount = 0;
        this.parentCompositeSymbols = new Set();

        this.xmlcache = null;
    }
    tplxml(minCount = 1, minLength = 1) {
        if (this.xmlcache) {
            return this.xmlcache;
        }

        let leftxml = this.left instanceof CompositeSymbol ? this.left.tplxml(minCount, minLength) : String(this.left);
        let rightxml = this.right instanceof CompositeSymbol ? this.right.tplxml(minCount, minLength) : String(this.right);

        // return this.strrepr with html span tags if count and length meet minimums
        if ((this.locs.size >= minCount) && (this.strrepr.length >= minLength) && ((this.parentCompositeSymbols.size > 1) || (this.toplevelcount > 0))) {
            this.xmlcache = `<span class="motif-instance" data-motifid='${this.compositesymbolID}'>${leftxml}${rightxml}</span>`;
        }
        else {
            this.xmlcache = `${leftxml}${rightxml}`;
        }
        return this.xmlcache;
    }
}


function symbolPairHash(left, right) {
    // hopefully `compsymb` doesnt appear in the text so that this is a good hash
    if (left instanceof CompositeSymbol) {
        left = `CoMpSyMb:${left.compositesymbolID}`;
    }
    if (right instanceof CompositeSymbol) {
        right = `CoMpSyMb:${right.compositesymbolID}`;
    }
    return `${left}_${right}`;
}

function symbolequalitycheck(left, right) {
    if (left instanceof CompositeSymbol && right instanceof CompositeSymbol) {
        return left.compositesymbolID === right.compositesymbolID;
    }
    else if (left instanceof CompositeSymbol || right instanceof SymbolLinkedListNode) {
        return false;
    }
    else {
        return left === right;
    }
}

class CompositeSymbolFactory {
    constructor() {
        this.instances = new Map();
        this.compsymbID = 0;
    }

    get_compositeSymbol(left, right) {
        let key = symbolPairHash(left, right);
        if (this.instances.has(key)) {
            return this.instances.get(key);
        }
        else {
            let compsymb = new CompositeSymbol(left, right, this.compsymbID++);
            this.instances.set(key, compsymb);
            if (left instanceof CompositeSymbol) {
                left.parentCompositeSymbols.add(compsymb);
            }
            if (right instanceof CompositeSymbol) {
                right.parentCompositeSymbols.add(compsymb);
            }
            return compsymb;
        }
    }
}

class SymbolLinkedListNode {
    constructor(symbol) {
        this.symbol = symbol;
        if (symbol instanceof CompositeSymbol) {
            symbol.locs.add(this);
            symbol.toplevelcount++;
        }
        this.prev = null;
        this.next = null;
        this.index = 0;

        this.strrepr = symbol.strrepr || symbol;
    }

    tplxml(minCount = 0, minLength = 1) {
        if (this.symbol instanceof CompositeSymbol) {
            return this.symbol.tplxml(minCount, minLength);
        }
        else {
            return this.symbol;
        }
    }

    join(rightnode) {
        if (this.next) {
            this.next.prev = null;
        }
        if (rightnode.prev) {
            rightnode.prev.next = null;
        }

        this.next = rightnode;
        rightnode.prev = this;

        rightnode.index = rightnode.prev.index + (rightnode.prev.symbol.length || 0);


        // not handled in this function is the creation of new disymb index entries
    }

    delete() {
        if (this.prev && this.prev.next === this) {
            throw new Error(`Cannot delete this node ${this.strrepr} as previous node ${this.prev.strrepr} is still connected`);
        }
        if (this.next && this.next.prev === this) {
            throw new Error("Cannot delete this node as next node is still connected");
        }
        this.prev = null;
        this.next = null

        if (this.symbol instanceof CompositeSymbol) {
            this.symbol.toplevelcount -= 1;
        }

    }



}


class Sequitur {
    constructor() {
        this.headnode = null;
        this.tailnode = null;

        // We keep track of all the symbols pairs (disymb) that has occured in the sequence so far
        // The moment a symbol pair appears again, we need to know where it had occured in the past sequence
        // This map helps us to quickly find the previous occurrence of a symbol pair
        this.disymb2nodepair = new Map();

        // This map stores all the rules that have been created so far
        // Rules map the symbol pair to the corresponding composite symbol
        this.disymb2compsymb = new Map();

        this.compositesymbolfactory = new CompositeSymbolFactory();
    }



    popLastNode() {
        if (this.tailnode) {
            let popnode = this.tailnode;
            this.tailnode = this.tailnode.prev;
            if (this.tailnode === null) {
                this.headnode = null;
            }
            else {
                this.disymb2nodepair.delete(symbolPairHash(this.tailnode.symbol, popnode.symbol));
            }

            popnode.delete();
            return popnode;
        }
    }

    replaceNodePair(node1, node2, cnode) {
        if (node1.next !== node2 || node2.prev !== node1) {
            throw new Error("Nodes are not consecutive.");
        }

        cnode.next = node2.next;
        if (node1 === this.headnode) {
            this.headnode = cnode;
        } else {
            node1.prev.join(cnode);
        }

        if (node2 === this.tailnode) {
            this.tailnode = cnode;
        } else {
            cnode.join(node2.next);
        }

        // deleting nodes
        node1.next = null;
        node2.prev = null;
        node1.delete()
        node2.delete()

    }

    replaceDisymb(sym1, sym2, compsymb) {
        const nodePair = this.disymb2nodepair.get(symbolPairHash(sym1, sym2));
        const [node1, node2] = nodePair;

        // Remove old disymbols
        if (node1.prev !== null) {
            this.disymb2nodepair.delete(symbolPairHash([node1.prev.symbol, node1.symbol]));
        }
        if (node2.next !== null) {
            this.disymb2nodepair.delete(symbolPairHash([node2.symbol, node2.next.symbol]));
        }

        // Create a new node and update links
        const cnode = new SymbolLinkedListNode(compsymb);
        this.replaceNodePair(node1, node2, cnode);

        // Add new disymbols
        if (cnode.prev !== null) {
            this.disymb2nodepair.set(symbolPairHash([cnode.prev.symbol, compsymb]), [cnode.prev, cnode]);
        }
        if (cnode.next !== null) {
            this.disymb2nodepair.set(symbolPairHash([compsymb, cnode.next.symbol]), [cnode, cnode.next]);
        }
    }

    substituteNodePair(node1, node2, cnode) {

        if (node1.next !== node2 || node2.prev !== node1) {
            throw new Error("Nodes are not consecutive.");
        }

        // Remove old disymbols
        if (node1.prev) {
            let key = symbolPairHash(node1.prev.symbol, node1.symbol);

            this.disymb2nodepair.delete(key);
        }
        if (node2.next) {
            let key = symbolPairHash(node2.symbol, node2.next.symbol);
            this.disymb2nodepair.delete(key);
        }

        let key = symbolPairHash(node1.symbol, node2.symbol);
        this.disymb2nodepair.delete(key);

        this.replaceNodePair(node1, node2, cnode);

        this.checkNodePair(cnode.prev);
        if (cnode.next) {
            this.checkNodePair(cnode);
        }

    }

    checkNodePair(node) {
        if (!node) return;
        const symbol = node.symbol;
        const nextsymbol = node.next.symbol;
        const key = symbolPairHash(symbol, nextsymbol);
        // case 1: a rule exists for node pair
        if (this.disymb2compsymb.has(key)) {
            const compsymb = this.disymb2compsymb.get(key);
            const cnode = new SymbolLinkedListNode(compsymb);
            this.substituteNodePair(node, node.next, cnode);
        }
        else {
            if (this.disymb2nodepair.has(key)) {
                const nodePair = this.disymb2nodepair.get(key);
                const [node1, node2] = nodePair;

                const compsymb = this.compositesymbolfactory.get_compositeSymbol(symbol, nextsymbol);
                this.disymb2compsymb.set(key, compsymb);

                if (node2 === node) {
                    const cnodepast = new SymbolLinkedListNode(compsymb);
                    this.substituteNodePair(node1, node2, cnodepast);
                }
                else {
                    const cnodepast = new SymbolLinkedListNode(compsymb);
                    this.substituteNodePair(node1, node2, cnodepast);
                    const cnodenow = new SymbolLinkedListNode(compsymb);
                    this.substituteNodePair(node, node.next, cnodenow);
                }
            }
        }
        this.disymb2nodepair.set(key, [node, node.next]);
    }

    addSymbol(symbol) {
        const node = new SymbolLinkedListNode(symbol);

        if (this.headnode === null) {
            this.headnode = node;
            this.tailnode = node;
        } else {
            this.tailnode.join(node);
            this.tailnode = node;
        }

        if (node.prev) {
            this.checkNodePair(node.prev);
        }
    }

    tplxml(minCount = 0, minLength = 1) {
        let out = '';
        let node = this.headnode;
        while (node !== null) {
            out += node.tplxml(minCount, minLength);
            node = node.next;
        }
        return out;
    }
}

